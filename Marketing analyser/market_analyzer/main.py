"""Command-line entry point: Tier 2/3 Market Expansion Profitability Analyzer."""
import argparse
import logging
import sys
from pathlib import Path
from typing import Dict, List, Optional

from data_loader import load_cities, load_config, validate_brand_inputs
from exceptions import AnalyzerError, InvalidInputError
from models import BrandInputs, Scenario
from report import (build_report, export_report, filter_cities, filter_results,
                    rank_results)
from scenarios import adjust_inputs, compare_scenarios, evaluate_cities, run_all_scenarios
from scoring import build_context

HERE = Path(__file__).resolve().parent
PROMPTS = [
    ("aov", "Average Order Value (> 0)"),
    ("conversion_rate", "Conversion rate (0 to 1)"),
    ("footfall_rate", "Footfall rate (0 to 1)"),
    ("setup_cost", "Setup cost (> 0)"),
    ("base_rent", "Annual base rent (>= 0)"),
    ("staff_cost", "Annual staff cost (>= 0)"),
    ("fixed_opex", "Other fixed opex (>= 0)"),
]


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Rank Tier 2/3 cities for retail expansion.")
    p.add_argument("--cities", default=str(HERE / "cities.csv"), help="path to cities CSV")
    p.add_argument("--config", default=str(HERE / "config.json"), help="path to brand-inputs JSON")
    p.add_argument("--interactive", action="store_true", help="type brand inputs instead of using config")
    p.add_argument("--scenario", choices=[s.value for s in Scenario], default="base",
                   help="scenario used for the main ranked table")
    p.add_argument("--sort", choices=["roi", "feasibility", "profit"], default="roi")
    p.add_argument("--tier", type=int, choices=[2, 3], help="only this tier")
    p.add_argument("--state", help="only this state")
    p.add_argument("--min-roi", type=float, help="only cities with ROI%% >= this")
    p.add_argument("--export", metavar="DIR", help="write txt/csv/json reports into DIR")
    p.add_argument("--formats", default="txt,csv,json", help="comma list of export formats")
    p.add_argument("--quiet", action="store_true", help="do not print the full report")
    return p


def prompt_inputs(defaults: Optional[BrandInputs]) -> BrandInputs:
    """Ask for each value, re-asking until it validates."""
    raw: Dict[str, object] = {}
    for key, label in PROMPTS:
        default = getattr(defaults, key) if defaults else None
        while True:
            shown = f" [{default:g}]" if default is not None else ""
            answer = input(f"{label}{shown}: ").strip() or (str(default) if default is not None else "")
            try:
                validate_brand_inputs({**{k: 1 for k, _ in PROMPTS}, key: answer})
            except InvalidInputError as exc:
                print(f"  Invalid: {exc}. Please try again.")
                continue
            raw[key] = answer
            break
    return validate_brand_inputs(raw)


def run(args: argparse.Namespace) -> int:
    cities = load_cities(args.cities)
    defaults = None
    if not args.interactive or Path(args.config).exists():
        try:
            defaults = load_config(args.config)
        except AnalyzerError:
            if not args.interactive:
                raise
    inputs = prompt_inputs(defaults) if args.interactive else defaults

    ctx = build_context(cities)                       # scores scaled against the full dataset
    selected = filter_cities(cities, args.tier, args.state)
    scenario = Scenario(args.scenario)
    results = evaluate_cities(selected, adjust_inputs(inputs, scenario), ctx)
    ranked = rank_results(filter_results(results, args.min_roi), args.sort)
    if not ranked:
        print("No cities match the selected filters. Try relaxing --tier, --state or --min-roi.")
        return 1

    kept = {r.city.city for r in ranked}
    runs = run_all_scenarios([c for c in selected if c.city in kept], inputs, ctx, args.sort)
    rows = compare_scenarios(runs)
    text = build_report(ranked, rows, inputs, scenario, args.sort)

    if not args.quiet:
        print(text)
    if args.export:
        formats = [f.strip().lower() for f in args.formats.split(",") if f.strip()]
        for path in export_report(ranked, rows, inputs, text, Path(args.export), formats):
            print(f"Exported: {path}")
    return 0


def main(argv: Optional[List[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    logging.basicConfig(level=logging.WARNING, format="WARNING: %(message)s", stream=sys.stderr)
    try:
        return run(args)
    except AnalyzerError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2
    except (KeyboardInterrupt, EOFError):
        print("\nCancelled.", file=sys.stderr)
        return 130


if __name__ == "__main__":
    sys.exit(main())
