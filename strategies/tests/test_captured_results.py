"""Checks the retained real public dataset, losing results and reproducibility."""
import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from grid_replay import read_candles, replay
from hk_strategy_core import Timeline
from verify_backtest_results import dataset, grid_metrics, native_metrics

DATA = Path(__file__).resolve().parents[1] / "data/20261105-20261107"


class TestCapturedResults(unittest.TestCase):
    def test_real_inputs_are_hash_bound_public_rows_with_unknown_snapshot_age(self):
        rows = dataset(DATA)
        self.assertGreater(len(rows), 0)
        self.assertTrue(all(row["source"]["viewer"] == "free" and row["snapshot_as_of"] is None
                            and row["delay_sec"] is None for row in rows.values()))

    def test_every_native_entry_is_bound_to_its_known_wall_and_cash_reconciles(self):
        rows = dataset(DATA)
        result = json.loads((DATA / "results/freqtrade.complete.json").read_text())
        metrics = native_metrics(result, rows)
        self.assertEqual(metrics["closed_positions"], len(result["strategy"]["HunterKillerWalls"]["trades"]))
        self.assertAlmostEqual(sum(value for day, value in metrics["daily_realized_quote"]), metrics["net_quote"])

    def test_every_grid_fill_reproduces_from_the_real_inputs_and_cash_reconciles(self):
        rows = dataset(DATA)
        expected = json.loads((DATA / "results/grid.complete.json").read_text())
        actual = replay(read_candles(DATA / "candles.csv"),
                        Timeline.read(DATA / "public-wall-proxy.jsonl", allow_publication_proxy=True))
        self.assertEqual(actual["fills"], expected["fills"])
        self.assertEqual(actual["net_quote"], expected["net_quote"])
        self.assertEqual(actual["daily_equity_change"], expected["daily_equity_change"])
        self.assertEqual(grid_metrics(expected, rows)["net_quote"], expected["net_quote"])


if __name__ == "__main__":
    unittest.main()
