"""Unit tests mirroring Section 14 of the vision document."""
import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import calculator as calc
from data_loader import load_cities, validate_brand_inputs
from exceptions import EmptyDatasetError, InvalidInputError, MissingColumnError
from models import BrandInputs, City, Scenario
from report import rank_results
from scenarios import compare_scenarios, evaluate_city, run_all_scenarios
from scoring import build_context

HEADER = ("city,state,tier,population,target_income_share,avg_household_income,"
          "rent_index,competition_level,infrastructure_score\n")
SAMPLE = BrandInputs(aov=2000, conversion_rate=0.25, footfall_rate=0.15,
                     setup_cost=20_000_000, base_rent=3_000_000,
                     staff_cost=3_500_000, fixed_opex=1_500_000)
WORKED = City("Example", "X", 2, 1_000_000, 0.20, 600_000, 0.80, 2, 7)
SMALL = City("Tiny", "X", 3, 100_000, 0.10, 400_000, 0.50, 1, 4)


def write_csv(text: str) -> str:
    fd, path = tempfile.mkstemp(suffix=".csv")
    with os.fdopen(fd, "w", encoding="utf-8") as fh:
        fh.write(text)
    return path


class TestCalculator(unittest.TestCase):
    def test_worked_example(self):
        r = evaluate_city(WORKED, SAMPLE, build_context([WORKED]))
        self.assertEqual(r.addressable_population, 200_000)
        self.assertEqual(r.annual_visitors, 30_000)
        self.assertEqual(r.revenue, 15_000_000)
        self.assertEqual(r.operating_cost, 7_400_000)
        self.assertEqual(r.net_profit, 7_600_000)
        self.assertAlmostEqual(r.payback_years, 2.63, places=2)
        self.assertAlmostEqual(r.roi_pct, 38.0)

    def test_loss_making_city(self):
        r = evaluate_city(SMALL, SAMPLE, build_context([SMALL]))
        self.assertLess(r.net_profit, 0)
        self.assertIsNone(r.payback_years)
        self.assertEqual(r.payback_label, "Never")
        self.assertLess(r.roi_pct, 0)
        self.assertFalse(r.is_profitable)

    def test_zero_profit_no_division_error(self):
        self.assertIsNone(calc.payback_period(1000, 0))


class TestValidation(unittest.TestCase):
    def test_conversion_rate_above_one(self):
        with self.assertRaises(InvalidInputError):
            validate_brand_inputs({**SAMPLE.__dict__, "conversion_rate": 1.5})

    def test_zero_setup_cost_rejected(self):
        with self.assertRaises(InvalidInputError):
            validate_brand_inputs({**SAMPLE.__dict__, "setup_cost": 0})

    def test_missing_column(self):
        path = write_csv("city,state\nA,B\n")
        with self.assertRaises(MissingColumnError) as ctx:
            load_cities(path)
        self.assertIn("population", str(ctx.exception))

    def test_empty_csv(self):
        with self.assertRaises(EmptyDatasetError):
            load_cities(write_csv(""))
        with self.assertRaises(EmptyDatasetError):
            load_cities(write_csv(HEADER))

    def test_bad_rows_skipped_and_duplicates_keep_first(self):
        path = write_csv(HEADER
                         + "Alpha,S,2,100000,0.2,500000,0.8,2,6\n"
                         + "alpha,S,2,999999,0.2,500000,0.8,2,6\n"     # duplicate
                         + "Beta,S,2,abc,0.2,500000,0.8,2,6\n"         # non-numeric
                         + "Gamma,S,2,-5,0.2,500000,0.8,2,6\n")        # negative
        with self.assertLogs("analyzer", level="WARNING"):
            cities = load_cities(path)
        self.assertEqual([c.city for c in cities], ["Alpha"])
        self.assertEqual(cities[0].population, 100000)

    def test_missing_file(self):
        from exceptions import DataFileError
        with self.assertRaises(DataFileError):
            load_cities("/nonexistent/cities.csv")


class TestScoringRankingScenarios(unittest.TestCase):
    def setUp(self):
        self.cities = load_cities(Path(__file__).resolve().parent.parent / "cities.csv")
        self.ctx = build_context(self.cities)

    def test_feasibility_bounds(self):
        for c in self.cities:
            score = evaluate_city(c, SAMPLE, self.ctx).feasibility
            self.assertTrue(0 <= score <= 100, (c.city, score))

    def test_competition_points(self):
        from scoring import competition_points
        self.assertEqual(competition_points(1), 20)
        self.assertEqual(competition_points(2), 16)
        self.assertEqual(competition_points(5), 4)

    def test_ranking_descending_roi(self):
        results = [evaluate_city(c, SAMPLE, self.ctx) for c in self.cities]
        ranked = rank_results(results)
        rois = [r.roi_pct for r in ranked]
        self.assertEqual(rois, sorted(rois, reverse=True))
        self.assertEqual([r.rank for r in ranked], list(range(1, len(ranked) + 1)))

    def test_scenario_ordering(self):
        runs = run_all_scenarios(self.cities, SAMPLE, self.ctx)
        for row in compare_scenarios(runs):
            self.assertLessEqual(row.roi[Scenario.CONSERVATIVE], row.roi[Scenario.BASE])
            self.assertLessEqual(row.roi[Scenario.BASE], row.roi[Scenario.OPTIMISTIC])


if __name__ == "__main__":
    unittest.main()
