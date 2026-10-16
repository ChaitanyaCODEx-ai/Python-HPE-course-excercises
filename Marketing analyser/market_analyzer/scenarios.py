"""Conservative / base / optimistic runs and rank-stability analysis (Section 8)."""
from dataclasses import dataclass, replace
from typing import Dict, List, Sequence

import calculator as calc
from models import BrandInputs, City, CityResult, Scenario
from report import rank_results
from scoring import DatasetContext, score_city

# Named, documented scenario multipliers
RATE_MULTIPLIER = {Scenario.CONSERVATIVE: 0.80, Scenario.BASE: 1.00, Scenario.OPTIMISTIC: 1.20}
COST_MULTIPLIER = {Scenario.CONSERVATIVE: 1.10, Scenario.BASE: 1.00, Scenario.OPTIMISTIC: 0.90}
ROBUST_TOP_N = 3   # a city in the top N under every scenario is flagged "robust"


def adjust_inputs(inputs: BrandInputs, scenario: Scenario) -> BrandInputs:
    """Scale conversion/footfall rates (capped at 1.0) and operating costs.

    Setup cost is a one-time capital figure and is left unchanged.
    """
    rate_m, cost_m = RATE_MULTIPLIER[scenario], COST_MULTIPLIER[scenario]
    return replace(
        inputs,
        conversion_rate=min(1.0, inputs.conversion_rate * rate_m),
        footfall_rate=min(1.0, inputs.footfall_rate * rate_m),
        base_rent=inputs.base_rent * cost_m,
        staff_cost=inputs.staff_cost * cost_m,
        fixed_opex=inputs.fixed_opex * cost_m,
    )


def evaluate_city(city: City, inputs: BrandInputs, ctx: DatasetContext, weights=None) -> CityResult:
    """Run every formula and the feasibility score for one city."""
    addr = calc.addressable_population(city.population, city.target_income_share)
    visitors = calc.annual_visitors(addr, inputs.footfall_rate)
    revenue = calc.annual_revenue(visitors, inputs.conversion_rate, inputs.aov)
    opex = calc.annual_operating_cost(inputs.base_rent, city.rent_index,
                                      inputs.staff_cost, inputs.fixed_opex)
    profit = calc.annual_net_profit(revenue, opex)
    score, breakdown = score_city(city, ctx, weights)
    return CityResult(
        city=city, addressable_population=addr, annual_visitors=visitors,
        revenue=revenue, operating_cost=opex, net_profit=profit,
        payback_years=calc.payback_period(inputs.setup_cost, profit),
        roi_pct=calc.roi_percent(profit, inputs.setup_cost),
        feasibility=score, score_breakdown=breakdown,
    )


def evaluate_cities(cities: Sequence[City], inputs: BrandInputs,
                    ctx: DatasetContext, weights=None) -> List[CityResult]:
    return [evaluate_city(c, inputs, ctx, weights) for c in cities]


def run_all_scenarios(cities: Sequence[City], inputs: BrandInputs,
                      ctx: DatasetContext, sort_by: str = "roi", weights=None) -> Dict[Scenario, List[CityResult]]:
    """Return a ranked result list for each scenario."""
    return {s: rank_results(evaluate_cities(cities, adjust_inputs(inputs, s), ctx, weights), sort_by)
            for s in Scenario}


@dataclass(frozen=True)
class ScenarioRow:
    city: str
    roi: Dict[Scenario, float]
    rank: Dict[Scenario, int]
    rank_change: int      # worst rank minus best rank across scenarios
    robust: bool


def compare_scenarios(runs: Dict[Scenario, List[CityResult]],
                      top_n: int = ROBUST_TOP_N) -> List[ScenarioRow]:
    """Build the scenario table, ordered by base-case rank."""
    rows = []
    for base in runs[Scenario.BASE]:
        name = base.city.city
        roi = {s: next(r.roi_pct for r in runs[s] if r.city.city == name) for s in Scenario}
        rank = {s: next(r.rank for r in runs[s] if r.city.city == name) for s in Scenario}
        rows.append(ScenarioRow(
            city=name, roi=roi, rank=rank,
            rank_change=max(rank.values()) - min(rank.values()),
            robust=all(rk <= top_n for rk in rank.values()),
        ))
    return rows
