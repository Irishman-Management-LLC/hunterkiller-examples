"""Offline OHLCV model of the paper grid, not a native Hummingbot backtest.

Decisions at completed candle closes create next-candle orders. Bars cannot
prove maker queue fills or intrabar ordering. The declared conservative rules
and complete fill log travel with every result, including every loss.
"""
from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

from hk_strategy_core import PUBLICATION_PROXY, Timeline, grid_quotes, positive


@dataclass(frozen=True)
class Candle:
    timestamp: int  # UTC open, seconds
    open: float
    high: float
    low: float
    close: float


def read_candles(path):
    candles = []
    with Path(path).open() as stream:
        for row in csv.DictReader(stream):
            stamp = int(row["timestamp"])
            values = [positive(row[key]) for key in ("open", "high", "low", "close")]
            candle = Candle(stamp, *values)
            if (stamp % 300 or (candles and stamp != candles[-1].timestamp + 300)
                    or candle.low > min(candle.open, candle.close)
                    or candle.high < max(candle.open, candle.close) or candle.low > candle.high):
                raise ValueError("Need contiguous coherent UTC 5 minute candles")
            candles.append(candle)
    if not candles:
        raise ValueError("No candles")
    return candles


def replay(candles, timeline, *, fee=0.001, slippage=0.0005, quote_budget=100.0):
    if not candles:
        raise ValueError("No candles")
    if not 0 <= fee < 0.1 or not 0 <= slippage < 0.1:
        raise ValueError("Invalid declared cost")
    quote_budget = positive(quote_budget)
    cash, inventory, basis = 1000.0, 0.0, 0.0
    fees, realized = 0.0, 0.0
    peak, drawdown = cash, 0.0
    plan, quotes, pending_exit = None, [], False
    plan_started = 0
    usable_bars = 0
    fills = []
    daily_equity = {}

    def fill(side, price, quantity, stamp, reason):
        nonlocal cash, inventory, basis, fees, realized
        if side == "buy":
            quantity = min(quantity, cash / (price * (1 + fee)))
        else:
            quantity = min(quantity, inventory)
        if quantity <= 1e-12:
            return
        cost = price * quantity
        charge = cost * fee
        net = None
        if side == "buy":
            inventory += quantity
            basis += cost + charge
            cash -= cost + charge
        else:
            allocated = basis * quantity / inventory
            net = cost - charge - allocated
            realized += net
            basis -= allocated
            inventory -= quantity
            cash += cost - charge
            if inventory < 1e-12:
                inventory, basis = 0.0, 0.0
        fees += charge
        fills.append({"bar_open": stamp, "side": side, "price": price, "amount": quantity,
                      "fee_quote": charge, "realized_net_quote": net, "reason": reason,
                      "wall_receipt_at": plan.available_at if plan else None})

    def close(price, stamp, reason):
        fill("sell", price * (1 - slippage), inventory, stamp, reason)

    for bar in candles:
        if pending_exit:
            close(bar.open, bar.timestamp, "unavailable_or_time_limit")
            plan, quotes, pending_exit = None, [], False
        if plan is not None:
            bids = [(price, amount) for side, price, amount in quotes if side == "buy" and bar.low < price]
            if bar.low <= plan.stop:
                # Worst ambiguous path: bids fill before the losing boundary;
                # no favorable ask fill is credited before the stop.
                for price, amount in bids:
                    fill("buy", price, amount, bar.timestamp, "bid_before_stop")
                close(min(bar.open, plan.stop), bar.timestamp, "wall_stop")
                plan, quotes = None, []
            elif bar.high > plan.target:
                # Do not credit new bid fills before a favorable same-bar exit.
                close(plan.target, bar.timestamp, "wall_target")
                plan, quotes = None, []
            elif bids:
                # One side per bar, buys first; never assume a same-bar round trip.
                for price, amount in bids:
                    fill("buy", price, amount, bar.timestamp, "bid_cross")
            else:
                for side, price, amount in quotes:
                    if side == "sell" and bar.high > price:
                        fill("sell", price, amount, bar.timestamp, "ask_cross")

        decision_at = bar.timestamp + 300
        sample = timeline.at(decision_at)
        usable_bars += int(sample is not None)
        if sample is None or (plan is not None and decision_at - plan_started >= 86400):
            quotes = []
            pending_exit = inventory > 0
            if inventory == 0:
                plan = None
        else:
            if plan is None or inventory == 0:
                plan = sample.long_plan(bar.close, decision_at)
                plan_started = decision_at
            quotes = grid_quotes(plan, bar.close, inventory, quote_budget=quote_budget) if plan else []
            if plan is not None and not plan.stop < bar.close < plan.target:
                pending_exit = inventory > 0

        equity = cash + inventory * bar.close
        day = datetime.fromtimestamp(bar.timestamp, timezone.utc).date().isoformat()
        daily_equity[day] = equity
        peak = max(peak, equity)
        drawdown = max(drawdown, peak - equity)
        if cash < -1e-8 or inventory < -1e-12:
            raise AssertionError("Paper portfolio went negative")

    close(candles[-1].close, candles[-1].timestamp + 300, "end_of_window")
    drawdown = max(drawdown, peak - cash)
    if abs(realized - (cash - 1000.0)) > 1e-7:
        raise AssertionError("Fill ledger does not reconcile to the final cash")
    daily_equity[datetime.fromtimestamp(candles[-1].timestamp, timezone.utc).date().isoformat()] = cash
    previous, daily = 1000.0, []
    for day, equity in daily_equity.items():
        daily.append({"utc_day": day, "net_quote": equity - previous, "ending_equity_quote": equity})
        previous = equity
    return {
        "model": "offline_5m_ohlcv_grid_replay_not_native_hummingbot",
        "input_basis": (PUBLICATION_PROXY if any(s is not None and s.tier == PUBLICATION_PROXY
                                               for s in timeline.samples) else "exact_api_receipts"),
        "window_start": candles[0].timestamp, "window_end": candles[-1].timestamp + 300,
        "bars": len(candles), "usable_input_bars": usable_bars,
        "missing_or_stale_input_bars": len(candles) - usable_bars,
        "initial_quote": 1000.0, "final_quote": cash, "net_quote": cash - 1000.0,
        "fees_quote": fees, "max_drawdown_quote": drawdown,
        "sell_fills_at_a_loss": sum(f["side"] == "sell" and f["realized_net_quote"] < 0 for f in fills),
        "fee_each_side": fee, "market_slippage": slippage, "quote_notional_budget": quote_budget,
        "assumptions": ["Next candle orders only", "Strict cross for passive fills",
                        "Buys first and one side per bar", "Losing boundary first on ambiguous bars",
                        "Market closes include slippage", "Every remaining position closed at window end",
                        "No queue, depth, latency, spread or partial fill reconstruction",
                        "Five minute refresh differs from the script's 30 second refresh"],
        "fills": fills,
        "daily_equity_change": daily,
        "daily_basis": "Close mark to market; final day includes the simulated end-of-window close costs",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("receipts", type=Path)
    parser.add_argument("candles", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--source-url", required=True, help="Actual candle source URL, retained with the result")
    parser.add_argument("--public-wall-proxy", action="store_true", help="Explicitly allow the labeled historical public-wall proxy")
    args = parser.parse_args()
    report = replay(read_candles(args.candles), Timeline.read(args.receipts, allow_publication_proxy=args.public_wall_proxy))
    report["inputs"] = {"receipts_sha256": hashlib.sha256(args.receipts.read_bytes()).hexdigest(),
                        "candles_sha256": hashlib.sha256(args.candles.read_bytes()).hexdigest(),
                        "candles_source_url": args.source_url}
    with args.output.open("x") as stream:
        json.dump(report, stream, indent=2, allow_nan=False)
        stream.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
