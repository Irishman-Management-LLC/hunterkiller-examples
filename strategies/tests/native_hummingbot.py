"""Run inside Hummingbot 2.17. Real config/order types, fixture market only."""
from collections import deque
from decimal import Decimal
from pathlib import Path
import sys
from types import SimpleNamespace
import unittest

from pydantic import ValidationError
from hummingbot.core.data_type.common import OrderType, TradeType
from hummingbot.core.data_type.trade_fee import AddedToCostTradeFee, DeductedFromReturnsTradeFee, TokenAmount
from hummingbot.core.event.events import OrderFilledEvent

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from hk_strategy_core import LongPlan
from hk_wall_grid import HKWallGrid, HKWallGridConfig


class FixtureConnector:
    def get_price(self, pair, is_buy):
        return Decimal("100.01") if is_buy else Decimal("99.99")

    def quantize_order_price(self, pair, price):
        return price.quantize(Decimal("0.01"))

    def quantize_order_amount(self, pair, amount):
        return amount.quantize(Decimal("0.000001"))


class TestHummingbotAdapter(unittest.TestCase):
    def test_native_config_is_paper_only_and_redacts_the_key(self):
        config = HKWallGridConfig(api_key="fixture-only")
        self.assertNotIn("fixture-only", repr(config))
        self.assertEqual(config.update_markets({}), {"binance_paper_trade": {"BTC-USDT"}})
        with self.assertRaises(ValidationError):
            HKWallGridConfig(exchange="binance")
        with self.assertRaises(ValidationError):
            HKWallGridConfig(trading_pair="ETH-USDT")

    def test_native_candidates_stay_passive_and_within_inventory(self):
        state = SimpleNamespace(config=HKWallGridConfig(), _inventory=Decimal("0.25"),
                                _plan=LongPlan(98, 103, 1),
                                connectors={"binance_paper_trade": FixtureConnector()})
        quotes = HKWallGrid.create_proposal(state, 100)
        self.assertEqual(len(quotes), 4)
        buys = [q for q in quotes if q.order_side == TradeType.BUY]
        sells = [q for q in quotes if q.order_side == TradeType.SELL]
        self.assertTrue(all(q.is_maker and q.order_type == OrderType.LIMIT for q in quotes))
        self.assertTrue(all(q.price < 100 for q in buys))
        self.assertTrue(all(q.price > 100 for q in sells))
        self.assertLessEqual(sum(q.amount for q in sells), Decimal("0.25"))

    def test_actual_fill_event_counts_only_own_orders_once(self):
        state = SimpleNamespace(_owned=deque(["owned"]), _fills=deque(maxlen=8192), _inventory=Decimal("0"))
        event = OrderFilledEvent(1, "owned", "BTC-USDT", TradeType.BUY, OrderType.LIMIT,
                                 Decimal("100"), Decimal("0.1"), AddedToCostTradeFee(),
                                 exchange_trade_id="fixture-fill")
        HKWallGrid.did_fill_order(state, event)
        HKWallGrid.did_fill_order(state, event)
        self.assertEqual(state._inventory, Decimal("0.1"))
        foreign = OrderFilledEvent(2, "foreign", "BTC-USDT", TradeType.BUY, OrderType.LIMIT,
                                   Decimal("100"), Decimal("1"), AddedToCostTradeFee(),
                                   exchange_trade_id="foreign-fill")
        HKWallGrid.did_fill_order(state, foreign)
        self.assertEqual(state._inventory, Decimal("0.1"))

    def test_base_fees_and_rounding_cannot_sell_foreign_inventory(self):
        state = SimpleNamespace(_owned=deque(["owned"]), _fills=deque(maxlen=8192), _inventory=Decimal("0"))
        event = OrderFilledEvent(1, "owned", "BTC-USDT", TradeType.BUY, OrderType.LIMIT,
                                 Decimal("100"), Decimal("0.1"),
                                 DeductedFromReturnsTradeFee(percent=Decimal("0.001"),
                                    flat_fees=[TokenAmount("BTC", Decimal("0.00001"))]),
                                 exchange_trade_id="fixture-fee")
        HKWallGrid.did_fill_order(state, event)
        self.assertEqual(state._inventory, Decimal("0.09989"))
        state.config = HKWallGridConfig()
        state._plan = LongPlan(98, 103, 1)
        state._inventory = Decimal("0.333333")
        state.connectors = {"binance_paper_trade": FixtureConnector()}
        quotes = HKWallGrid.create_proposal(state, 100)
        self.assertLessEqual(sum(q.amount for q in quotes if q.order_side == TradeType.SELL), state._inventory)
        self.assertLessEqual(sum(q.amount * q.price for q in quotes if q.order_side == TradeType.BUY),
                             Decimal("100") - state._inventory * 100)

    def test_stop_intent_survives_cancellation_and_price_reentry(self):
        calls = []
        state = SimpleNamespace(current_timestamp=1000, _feed=SimpleNamespace(next_poll=2000,
            timeline=SimpleNamespace(at=lambda now: object())), _refresh_task=None,
            config=HKWallGridConfig(), connectors={"binance_paper_trade": SimpleNamespace(
                get_price_by_type=lambda *a: Decimal("100"))}, _flatten_order=None, _closing=True,
            _inventory=Decimal("0.1"), _active_orders=lambda: [], _flatten=lambda orders: calls.append("close"))
        HKWallGrid.on_tick(state)
        self.assertEqual(calls, ["close"])
        self.assertTrue(state._closing)


if __name__ == "__main__":
    unittest.main()
