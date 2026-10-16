"""Local web server: serves the web/ front-end and a JSON API built on the project modules.

Run:  python server.py   ->  opens http://localhost:8000
"""
import argparse
import json
import logging
import tempfile
import webbrowser
from dataclasses import asdict
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

from data_loader import load_cities, parse_city_row, validate_brand_inputs
from exceptions import AnalyzerError, EmptyDatasetError, InvalidInputError
from models import Scenario
from report import (build_report, export_report, filter_cities, rank_results, summary_stats)
from scenarios import adjust_inputs, compare_scenarios, evaluate_cities, run_all_scenarios
from scoring import build_context

ROOT = Path(__file__).resolve().parent
WEB = ROOT / "web"
TYPES = {".html": "text/html", ".css": "text/css", ".js": "text/javascript", ".json": "application/json"}


def result_json(r):
    return {"name": r.city.city, "state": r.city.state, "tier": r.city.tier, "rank": r.rank,
            "addr": r.addressable_population, "vis": r.annual_visitors, "revenue": r.revenue,
            "opex": r.operating_cost, "profit": r.net_profit, "payback": r.payback_years,
            "roi": r.roi_pct, "feas": r.feasibility,
            "bd": [[n, round(e, 1), round(m, 1), why] for n, e, m, why in r.score_breakdown]}


def parse_rows(rows):
    """Validate raw city dicts with the same rules as the CSV loader."""
    cities, errors, seen = [], [], set()
    for i, row in enumerate(rows, 1):
        label = row.get("city") or f"row {i}"
        try:
            c = parse_city_row({k: str(v) for k, v in row.items()})
        except (InvalidInputError, KeyError) as exc:
            errors.append(f"{label}: {exc}")
            continue
        if c.city.casefold() in seen:
            errors.append(f"{c.city}: duplicate ignored")
            continue
        seen.add(c.city.casefold())
        cities.append(c)
    return cities, errors


def analyze(p):
    inputs = validate_brand_inputs(p["inputs"])
    cities, errors = parse_rows(p["cities"])
    if not cities:
        raise EmptyDatasetError("No valid cities. Add a city or upload a CSV in the Data tab.")
    ctx, w = build_context(cities), p.get("weights")
    tier = int(p["tier"]) if str(p.get("tier", "all")).isdigit() else None
    state = p.get("state") if p.get("state") not in (None, "all") else None
    sel = filter_cities(cities, tier, state)
    scen, sort = Scenario(p.get("scenario", "base")), p.get("sort", "roi")
    out = {"errors": errors, "states": sorted({c.state for c in cities}), "results": [], "scenarios": [],
           "used": {}, "summary": None, "export": None}
    if not sel:
        return out
    used = adjust_inputs(inputs, scen)
    ranked = rank_results(evaluate_cities(sel, used, ctx, w), sort)
    rows = compare_scenarios(run_all_scenarios(sel, inputs, ctx, sort, w))
    out.update(results=[result_json(r) for r in ranked], used=asdict(used) | {"setup": inputs.setup_cost},
               summary=summary_stats(ranked),
               scenarios=[{"city": r.city, "roi": [r.roi[s] for s in Scenario],
                           "rank": [r.rank[s] for s in Scenario], "change": r.rank_change,
                           "robust": r.robust} for r in rows])
    if p.get("export"):
        text = build_report(ranked, rows, inputs, scen, sort)
        with tempfile.TemporaryDirectory() as tmp:
            out["export"] = {f.suffix[1:]: f.read_text(encoding="utf-8") for f in
                             export_report(ranked, rows, inputs, text, Path(tmp))}
    return out


def parse_csv(text):
    class Grab(logging.Handler):
        msgs = []
        def emit(self, rec):
            self.msgs.append(rec.getMessage())
    grab, log = Grab(), logging.getLogger("analyzer")
    grab.msgs = []
    log.addHandler(grab)
    try:
        with tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False, encoding="utf-8") as fh:
            fh.write(text)
        cities = load_cities(fh.name)
    finally:
        log.removeHandler(grab)
        Path(fh.name).unlink(missing_ok=True)
    return {"cities": [asdict(c) for c in cities], "warnings": grab.msgs}


def defaults():
    return {"cities": [asdict(c) for c in load_cities(ROOT / "cities.csv")],
            "inputs": json.loads((ROOT / "config.json").read_text())}


class Handler(BaseHTTPRequestHandler):
    def send(self, code, body, ctype="application/json"):
        data = body if isinstance(body, bytes) else json.dumps(body).encode()
        self.send_response(code)
        self.send_header("Content-Type", ctype + "; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        path = urlparse(self.path).path
        if path == "/api/defaults":
            return self.send(200, defaults())
        f = (WEB / (path.lstrip("/") or "index.html")).resolve()
        if WEB not in f.parents or not f.is_file():
            return self.send(404, {"error": "Not found"})
        self.send(200, f.read_bytes(), TYPES.get(f.suffix, "application/octet-stream"))

    def do_POST(self):
        routes = {"/api/analyze": analyze, "/api/parse-csv": lambda p: parse_csv(p["text"])}
        try:
            body = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))) or b"{}")
            self.send(200, routes[urlparse(self.path).path](body))
        except AnalyzerError as exc:
            self.send(400, {"error": str(exc)})
        except (KeyError, ValueError, TypeError) as exc:
            self.send(400, {"error": f"Bad request: {exc}"})

    def log_message(self, *args):
        pass


def main():
    ap = argparse.ArgumentParser(description="Run the analyzer web app.")
    ap.add_argument("--port", type=int, default=8000)
    ap.add_argument("--no-browser", action="store_true")
    args = ap.parse_args()
    server = ThreadingHTTPServer(("127.0.0.1", args.port), Handler)
    url = f"http://localhost:{args.port}"
    print(f"Analyzer running at {url}  (Ctrl+C to stop)")
    if not args.no_browser:
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")


if __name__ == "__main__":
    main()
