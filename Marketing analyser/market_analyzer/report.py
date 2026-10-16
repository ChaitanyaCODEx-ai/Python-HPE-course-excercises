"""Ranking, filtering, formatting, and export (Sections 9 and 15)."""
import csv
import json
import statistics
from dataclasses import replace
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Sequence

from models import BrandInputs, City, CityResult, Scenario

SORT_KEYS = {
    "roi": lambda r: (r.roi_pct, r.feasibility),
    "feasibility": lambda r: (r.feasibility, r.roi_pct),
    "profit": lambda r: (r.net_profit, r.feasibility),
}
LIMITATIONS = ("Results are estimates from stated assumptions, not predictions or financial advice. "
               "City data is static and illustrative; one store per city and uniform brand inputs are "
               "assumed; seasonality, inflation, and competitor reactions are not modeled.")


# ---------- ranking & filtering ----------
def rank_results(results: Sequence[CityResult], sort_by: str = "roi") -> List[CityResult]:
    ordered = sorted(results, key=SORT_KEYS[sort_by], reverse=True)
    return [replace(r, rank=i) for i, r in enumerate(ordered, start=1)]


def filter_cities(cities: Sequence[City], tier: Optional[int] = None,
                  state: Optional[str] = None) -> List[City]:
    return [c for c in cities
            if (tier is None or c.tier == tier)
            and (state is None or c.state.casefold() == state.strip().casefold())]


def filter_results(results: Sequence[CityResult], min_roi: Optional[float] = None) -> List[CityResult]:
    return [r for r in results if min_roi is None or r.roi_pct >= min_roi]


# ---------- formatting ----------
def money(value: float) -> str:
    return f"{value / 1e6:.1f}M"


def _fmt_roi(value: float) -> str:
    return f"{value:.1f}%"


def _header(inputs: BrandInputs, scenario: Scenario, sort_by: str, stamp: str) -> List[str]:
    return [
        "=" * 100,
        "TIER 2/3 MARKET EXPANSION PROFITABILITY ANALYZER",
        f"Generated: {stamp}   |   Main ranking scenario: {scenario.value}   |   Sorted by: {sort_by}",
        "=" * 100,
        "ASSUMPTIONS USED (base inputs)",
        f"  AOV {inputs.aov:,.0f} | conversion {inputs.conversion_rate:.0%} | footfall {inputs.footfall_rate:.0%}",
        f"  setup cost {inputs.setup_cost:,.0f} | base rent {inputs.base_rent:,.0f} | "
        f"staff {inputs.staff_cost:,.0f} | fixed opex {inputs.fixed_opex:,.0f}",
        "",
    ]


def _ranked_table(ranked: Sequence[CityResult]) -> List[str]:
    head = (f"{'Rank':<5}{'City':<16}{'Tier':<6}{'Revenue':>10}{'Net Profit':>12}"
            f"{'Payback':>12}{'ROI':>9}{'Feasibility':>13}")
    lines = ["RANKED TABLE", head, "-" * len(head)]
    for r in ranked:
        flag = "" if r.is_profitable else "  <-- UNPROFITABLE"
        lines.append(f"{r.rank:<5}{r.city.city:<16}{'T' + str(r.city.tier):<6}{money(r.revenue):>10}"
                     f"{money(r.net_profit):>12}{r.payback_label:>12}{_fmt_roi(r.roi_pct):>9}"
                     f"{r.feasibility:>9.1f}/100{flag}")
    return lines + [""]


def _explanations(ranked: Sequence[CityResult], inputs: BrandInputs) -> List[str]:
    lines = ["PER-CITY EXPLANATION (formula steps and feasibility breakdown)"]
    for r in ranked:
        c = r.city
        lines += [
            "", f"#{r.rank} {c.city}, {c.state} (Tier {c.tier})",
            f"  Addressable population = {c.population:,.0f} x {c.target_income_share:.2f} = {r.addressable_population:,.0f}",
            f"  Annual visitors        = {r.addressable_population:,.0f} x {inputs.footfall_rate:.3f} = {r.annual_visitors:,.0f}",
            f"  Annual revenue         = {r.annual_visitors:,.0f} x {inputs.conversion_rate:.3f} x {inputs.aov:,.0f} = {r.revenue:,.0f}",
            f"  Operating cost         = ({inputs.base_rent:,.0f} x {c.rent_index:.2f}) + {inputs.staff_cost:,.0f} + {inputs.fixed_opex:,.0f} = {r.operating_cost:,.0f}",
            f"  Net profit             = {r.revenue:,.0f} - {r.operating_cost:,.0f} = {r.net_profit:,.0f}",
            f"  Payback                = {inputs.setup_cost:,.0f} / {r.net_profit:,.0f} = {r.payback_label}"
            if r.is_profitable else
            f"  Payback                = Never (net profit is {r.net_profit:,.0f}, not positive)",
            f"  ROI                    = {r.net_profit:,.0f} / {inputs.setup_cost:,.0f} x 100 = {r.roi_pct:.1f}%",
            f"  Feasibility {r.feasibility:.1f}/100:",
        ]
        lines += [f"    - {n}: {e:g}/{m:g} ({why})" for n, e, m, why in r.score_breakdown]
    return lines + [""]


def _scenario_table(rows) -> List[str]:
    head = (f"{'City':<16}{'Conservative':>14}{'Base':>9}{'Optimistic':>12}"
            f"{'Ranks (C/B/O)':>16}{'Change':>8}  Robust?")
    lines = ["SCENARIO ANALYSIS (ROI and rank in each case)", head, "-" * len(head)]
    for row in rows:
        c, b, o = (row.rank[s] for s in (Scenario.CONSERVATIVE, Scenario.BASE, Scenario.OPTIMISTIC))
        lines.append(f"{row.city:<16}{_fmt_roi(row.roi[Scenario.CONSERVATIVE]):>14}"
                     f"{_fmt_roi(row.roi[Scenario.BASE]):>9}{_fmt_roi(row.roi[Scenario.OPTIMISTIC]):>12}"
                     f"{f'{c}/{b}/{o}':>16}{row.rank_change:>8}  {'ROBUST' if row.robust else '-'}")
    lines.append("Robust = in the top 3 by ROI under all three scenarios.")
    return lines + [""]


def summary_stats(ranked: Sequence[CityResult]) -> Dict[str, object]:
    rois = [r.roi_pct for r in ranked]
    return {
        "cities_analyzed": len(ranked),
        "profitable": sum(r.is_profitable for r in ranked),
        "loss_making": sum(not r.is_profitable for r in ranked),
        "best_city": ranked[0].city.city if ranked else None,
        "best_roi_pct": round(max(rois), 2),
        "worst_city": min(ranked, key=lambda r: r.roi_pct).city.city,
        "worst_roi_pct": round(min(rois), 2),
        "mean_roi_pct": round(statistics.mean(rois), 2),
        "median_roi_pct": round(statistics.median(rois), 2),
    }


def _summary(ranked: Sequence[CityResult]) -> List[str]:
    s = summary_stats(ranked)
    best = max(ranked, key=lambda r: r.roi_pct)
    worst = min(ranked, key=lambda r: r.roi_pct)
    return ["SUMMARY",
            f"  Cities analyzed: {s['cities_analyzed']}  |  Profitable: {s['profitable']}  |  Loss-making: {s['loss_making']}",
            f"  Best ROI : {best.city.city} ({best.roi_pct:.1f}%)   Worst ROI: {worst.city.city} ({worst.roi_pct:.1f}%)",
            f"  Mean ROI : {s['mean_roi_pct']:.1f}%   Median ROI: {s['median_roi_pct']:.1f}%",
            "", "LIMITATIONS", f"  {LIMITATIONS}"]


def build_report(ranked: Sequence[CityResult], scenario_rows, inputs: BrandInputs,
                 scenario: Scenario = Scenario.BASE, sort_by: str = "roi",
                 timestamp: Optional[datetime] = None) -> str:
    stamp = (timestamp or datetime.now()).strftime("%Y-%m-%d %H:%M:%S")
    lines = (_header(inputs, scenario, sort_by, stamp) + _ranked_table(ranked)
             + _explanations(ranked, inputs) + _scenario_table(scenario_rows) + _summary(ranked))
    return "\n".join(lines) + "\n"


# ---------- export ----------
def _result_row(r: CityResult) -> Dict[str, object]:
    return {
        "rank": r.rank, "city": r.city.city, "state": r.city.state, "tier": r.city.tier,
        "revenue": round(r.revenue, 2), "operating_cost": round(r.operating_cost, 2),
        "net_profit": round(r.net_profit, 2),
        "payback_years": "Never" if r.payback_years is None else round(r.payback_years, 2),
        "roi_pct": round(r.roi_pct, 2), "feasibility": r.feasibility,
    }


def export_report(ranked: Sequence[CityResult], scenario_rows, inputs: BrandInputs,
                  text: str, out_dir: Path, formats: Sequence[str] = ("txt", "csv", "json"),
                  timestamp: Optional[datetime] = None) -> List[Path]:
    """Write the report in the requested formats; return the paths created."""
    now = timestamp or datetime.now()
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    base = out_dir / f"report_{now:%Y%m%d_%H%M%S}"
    written = []
    if "txt" in formats:
        p = base.with_suffix(".txt"); p.write_text(text, encoding="utf-8"); written.append(p)
    if "csv" in formats:
        p = base.with_suffix(".csv")
        rows = [_result_row(r) for r in ranked]
        with p.open("w", newline="", encoding="utf-8") as fh:
            writer = csv.DictWriter(fh, fieldnames=list(rows[0]))
            writer.writeheader(); writer.writerows(rows)
        written.append(p)
    if "json" in formats:
        p = base.with_suffix(".json")
        payload = {
            "generated": now.isoformat(timespec="seconds"),
            "inputs": inputs.__dict__,
            "ranked": [_result_row(r) | {"feasibility_breakdown": [
                {"factor": n, "points": e, "max": m, "reason": why} for n, e, m, why in r.score_breakdown]}
                for r in ranked],
            "scenarios": [{"city": row.city, "roi_pct": {s.value: round(v, 2) for s, v in row.roi.items()},
                           "rank": {s.value: v for s, v in row.rank.items()},
                           "rank_change": row.rank_change, "robust": row.robust} for row in scenario_rows],
            "summary": summary_stats(ranked),
        }
        p.write_text(json.dumps(payload, indent=2), encoding="utf-8"); written.append(p)
    return written
