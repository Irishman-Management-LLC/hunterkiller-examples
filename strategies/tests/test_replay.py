"""Synthetic OHLCV fixtures verify the replay model, not any market result."""
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from grid_replay import Candle, read_candles, replay
from hk_strategy_core import Timeline, grid_quotes, LongPlan, parse_snapshot
from test_core import fixture, T


def timeline():
    result = Timeline()
    result.append(T, parse_snapshot(fixture(), T, "BTCUSDT"))
    return result


class TestGridReplay(unittest.TestCase):
    def test_no_same_bar_order_from_a_close_or_future_wall(self):
        # The first bar crosses both boundaries before the receipt is available.
        bars = [Candle(int(T - 300), 100, 104, 97, 100), Candle(int(T), 100, 101, 99, 100)]
        report = replay(bars, timeline())
        self.assertTrue(report["fills"])
        self.assertTrue(all(fill["bar_open"] >= T for fill in report["fills"]))

    def test_ambiguous_bar_keeps_the_loss_and_both_fees(self):
        bars = [Candle(int(T - 300), 100, 101, 99, 100), Candle(int(T), 100, 104, 97, 100)]
        report = replay(bars, timeline())
        self.assertLess(report["net_quote"], 0)
        self.assertEqual(report["sell_fills_at_a_loss"], 1)
        self.assertGreater(report["fees_quote"], 0.19)
        self.assertEqual(report["fills"][-1]["reason"], "wall_stop")
        self.assertAlmostEqual(sum(fill["realized_net_quote"] or 0 for fill in report["fills"]), report["net_quote"])

    def test_a_touch_without_a_cross_does_not_claim_a_maker_fill(self):
        top_bid = grid_quotes(LongPlan(98, 103, T), 100, 0)[0][1]
        bars = [Candle(int(T - 300), 100, 101, 99, 100), Candle(int(T), 100, 101, top_bid, 100)]
        report = replay(bars, timeline())
        self.assertEqual(report["fills"], [])
        self.assertEqual(report["net_quote"], 0)

    def test_missing_inputs_are_counted_without_inventing_trades(self):
        bars = [Candle(int(T - 300), 100, 101, 99, 100)]
        report = replay(bars, Timeline())
        self.assertEqual(report["missing_or_stale_input_bars"], 1)
        self.assertEqual(report["usable_input_bars"], 0)
        self.assertEqual(report["fills"], [])

    def test_feed_gap_closes_at_the_next_open_with_market_costs(self):
        feed = timeline()
        feed.append(T + 1, None)
        bars = [Candle(int(T - 300), 100, 101, 99, 100),
                Candle(int(T), 100, 101, 99, 100),
                Candle(int(T + 300), 99, 100, 98.5, 99)]
        report = replay(bars, feed)
        close = report["fills"][-1]
        self.assertEqual(close["reason"], "unavailable_or_time_limit")
        self.assertEqual(close["bar_open"], T + 300)
        self.assertLess(close["price"], 99)
        self.assertGreater(close["fee_quote"], 0)

    def test_incoherent_or_missing_candles_cannot_be_a_result(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "fixture.csv"
            for rows in (f"{int(T)},100,99,98,100\n", f"{int(T)},100,101,99,100\n{int(T+600)},100,101,99,100\n"):
                path.write_text("timestamp,open,high,low,close\n" + rows)
                with self.assertRaises(ValueError):
                    read_candles(path)
        with self.assertRaises(ValueError):
            replay([], Timeline())


if __name__ == "__main__":
    unittest.main()
