# Tier 2/3 Market Expansion Profitability Analyzer

A pure-standard-library Python CLI that ranks Tier 2/3 cities for retail expansion by
revenue, profit, payback, ROI and a 100-point feasibility score, with conservative /
base / optimistic scenarios. Every number is shown with its formula.

## Web app (recommended demo)
    python server.py            # opens http://localhost:8000  (use --port 9000 to change)
Four tabs: **Explore** (live sliders, bubble chart, sortable table, formula drill-down, scenario
robustness, feasibility weight tuner), **Compare** (radar chart of up to 3 pinned cities),
**Beat the model** (pick your top 3, then see how they really perform), **Your data**
(add a city, drag-and-drop a CSV, export txt/csv/json). All maths runs in the Python modules;
the browser only draws. Files: `server.py` (API) and `web/` (index.html, style.css, app.js).
Needs internet only for the Google Fonts (falls back to system fonts offline).

## Command line (Python 3.9+, no installs)
    python main.py                                  # full report using cities.csv + config.json
    python main.py --interactive                    # type your own brand inputs (validated, re-asks on bad values)
    python main.py --tier 3 --min-roi 0             # filters: --tier, --state, --min-roi
    python main.py --sort feasibility               # sort: roi | feasibility | profit
    python main.py --scenario conservative          # main table under another scenario
    python main.py --export out --formats txt,csv,json --quiet
    python -m unittest discover -s tests -v         # run the tests

## Formulas
addressable = population x target_income_share; visitors = addressable x footfall_rate;
revenue = visitors x conversion_rate x AOV; operating cost = base_rent x rent_index + staff + fixed_opex;
net profit = revenue - operating cost; payback = setup_cost / net profit ("Never" if <= 0);
ROI % = net profit / setup_cost x 100.

## Feasibility score (100)
Market size 25 (addressable pop vs largest city) | Income 25 (vs highest income) |
Competition 20 (24 - 4 x level) | Rent affordability 15 (lowest rent index / city rent index) |
Infrastructure 15 (score / 10 x 15). Scaled against the full dataset, even when filters are used.

## Scenarios (constants in scenarios.py)
Conservative: conversion & footfall x0.8 (capped at 1.0), operating costs x1.1.
Optimistic: x1.2 and x0.9. Setup cost is one-time capital and is unchanged.
A city in the top 3 by ROI in all three scenarios is flagged ROBUST.

## Data
cities.csv is ILLUSTRATIVE (rounded, approximate figures for demonstration). Replace with
Census / market-report data and document each column's source here before real use.

## Limitations
Estimates from stated assumptions, not financial advice. Static data; one store per city;
uniform brand inputs; no seasonality, inflation or competitor reaction.
