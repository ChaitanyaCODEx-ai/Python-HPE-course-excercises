"""Tests for the weights feature and the JSON API layer."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import server
from exceptions import EmptyDatasetError, InvalidInputError
from scoring import scaled_weights


class TestWeights(unittest.TestCase):
    def test_default_weights_total_100(self):
        self.assertEqual(sum(scaled_weights().values()), 100)

    def test_custom_weights_rescale_to_100(self):
        w = scaled_weights({"market": 50, "income": 50, "competition": 0, "rent": 0, "infra": 0})
        self.assertAlmostEqual(sum(w.values()), 100)
        self.assertEqual(w["market"], 50)

    def test_zero_weights_fall_back_to_defaults(self):
        self.assertEqual(scaled_weights({k: 0 for k in scaled_weights()}), scaled_weights())


class TestApi(unittest.TestCase):
    def setUp(self):
        self.d = server.defaults()

    def test_analyze_returns_ranked_results_and_scenarios(self):
        out = server.analyze({**self.d, "scenario": "base"})
        rois = [r["roi"] for r in out["results"]]
        self.assertEqual(rois, sorted(rois, reverse=True))
        self.assertEqual(len(out["scenarios"]), len(out["results"]))
        for r in out["results"]:
            self.assertTrue(0 <= r["feas"] <= 100)

    def test_feasibility_never_exceeds_100_with_custom_weights(self):
        out = server.analyze({**self.d, "weights": {"market": 1, "income": 0, "competition": 0, "rent": 0, "infra": 0}})
        self.assertTrue(all(0 <= r["feas"] <= 100 for r in out["results"]))

    def test_bad_city_reported_not_crashing(self):
        bad = {"city": "Ghost", "state": "X", "tier": 2, "population": -5}
        out = server.analyze({**self.d, "cities": self.d["cities"] + [bad]})
        self.assertTrue(any(e.startswith("Ghost") for e in out["errors"]))

    def test_invalid_brand_input_raises(self):
        with self.assertRaises(InvalidInputError):
            server.analyze({**self.d, "inputs": {**self.d["inputs"], "conversion_rate": 1.5}})

    def test_no_valid_cities_raises(self):
        with self.assertRaises(EmptyDatasetError):
            server.analyze({**self.d, "cities": []})

    def test_filter_with_no_match_returns_empty(self):
        out = server.analyze({**self.d, "state": "Atlantis"})
        self.assertEqual(out["results"], [])

    def test_export_bundle(self):
        out = server.analyze({**self.d, "export": True})
        self.assertEqual(sorted(out["export"]), ["csv", "json", "txt"])

    def test_parse_csv_collects_warnings(self):
        text = ("city,state,tier,population,target_income_share,avg_household_income,rent_index,"
                "competition_level,infrastructure_score\nA,S,2,100000,0.2,500000,0.8,2,6\nB,S,2,oops,0.2,500000,0.8,2,6\n")
        out = server.parse_csv(text)
        self.assertEqual(len(out["cities"]), 1)
        self.assertEqual(len(out["warnings"]), 1)


if __name__ == "__main__":
    unittest.main()
