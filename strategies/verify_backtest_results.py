"""Independent artifact checks for the fixed historical public-wall proxy."""
from __future__ import annotations

import argparse
from decimal import Decimal
import hashlib
import json
from pathlib import Path


def require(value, message="Backtest artifact mismatch"):
    if not value:
        raise ValueError(message)


def dataset(data):
    manifest = json.loads((data / "dataset.manifest.json").read_text())
    if manifest["kind"] != "historical_public_wall_proxy":
        raise AssertionError("Unexpected dataset basis")
    allowed = {"public-wall-proxy.manifest.json", "instrument.raw.json", "candles.receipt.json",
               "candles.csv", "instrument.receipt.json", "public-wall-proxy.jsonl", "bybit/BTC_USDT-5m.json"}
    require(set(manifest["inputs"]) == allowed, "Unexpected dataset file list")
    for name, digest in manifest["inputs"].items():
        require(not (data / name).is_symlink() and (data / name).resolve().is_relative_to(data.resolve()),
                "Dataset paths must stay inside the input directory")
        if hashlib.sha256((data / name).read_bytes()).hexdigest() != digest:
            raise AssertionError("Input hash mismatch: " + name)
    rows = [json.loads(line) for line in (data / "public-wall-proxy.jsonl").read_text().splitlines()]
    for row in rows:
        require(row["kind"] == "historical_public_wall_proxy" and row["source"]["viewer"] == "free")
        require(row["snapshot_as_of"] is None and row["delay_sec"] is None)
        require(row["received_at"] == row["published_at"] + 1)
        if "error" not in row:
            for key in ("below", "above"):
                wall = row["nearest"][key]
                if wall is not None:
                    require(any(abs(w["price"] - wall["price"]) < 1e-6 and w["side"] == wall["side"]
                                for w in row["walls"]))
    return {row["received_at"]: row for row in rows if "error" not in row}


def native_metrics(result, rows):
    stats = result["strategy"]["HunterKillerWalls"]
    trades = stats["trades"]
    require(len(trades) == stats["total_trades"])
    require(abs(sum(t["profit_abs"] for t in trades) - stats["profit_total_abs"]) < 1e-7)
    require(abs(stats["final_balance"] - 1000 - stats["profit_total_abs"]) < 1e-7)
    for trade in trades:
        prefix, stop, target, receipt = trade["enter_tag"].split(":")
        require(prefix == "hk")
        row = rows[float(receipt)]
        require(abs(row["nearest"]["below"]["price"] - float(stop)) < 1e-6)
        require(abs(row["nearest"]["above"]["price"] - float(target)) < 1e-6)
        require(0 <= trade["open_timestamp"] / 1000 - float(receipt) <= 900)
        require(not trade["is_short"] and trade["leverage"] == 1)
        require(trade["fee_open"] == trade["fee_close"] == 0.0015)
    return {"net_quote": stats["profit_total_abs"], "closed_positions": len(trades),
            "losing_positions": sum(t["profit_abs"] < 0 for t in trades),
            "daily_realized_quote": stats["daily_profit"]}


def grid_metrics(result, rows):
    cash, inventory = Decimal("1000"), Decimal("0")
    for fill in result["fills"]:
        price, amount, fee = [Decimal(str(fill[key])) for key in ("price", "amount", "fee_quote")]
        require(fill["wall_receipt_at"] in rows)
        require(fill["wall_receipt_at"] <= fill["bar_open"])
        if fill["side"] == "buy":
            cash -= price * amount + fee
            inventory += amount
        else:
            cash += price * amount - fee
            inventory -= amount
        require(inventory > Decimal("-0.0000000001"))
    require(abs(inventory) < Decimal("0.0000000001"))
    require(abs(cash - Decimal(str(result["final_quote"]))) < Decimal("0.0000001"))
    require(abs(float(cash - 1000) - result["net_quote"]) < 1e-7)
    return {"net_quote": result["net_quote"], "fill_events": len(result["fills"]),
            "losing_sell_fills": result["sell_fills_at_a_loss"],
            "daily_equity_change": result["daily_equity_change"]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("data", type=Path)
    parser.add_argument("fresh_native", type=Path)
    args = parser.parse_args()
    rows = dataset(args.data)
    actual = json.loads(args.fresh_native.read_text())
    expected = json.loads((args.data / "results/freqtrade.complete.json").read_text())
    a, b = native_metrics(actual, rows), native_metrics(expected, rows)
    require(abs(a["net_quote"] - b["net_quote"]) < 1e-7)
    require(a["closed_positions"] == b["closed_positions"] and a["losing_positions"] == b["losing_positions"])
    for left, right in zip(actual["strategy"]["HunterKillerWalls"]["trades"],
                           expected["strategy"]["HunterKillerWalls"]["trades"]):
        require(left["enter_tag"] == right["enter_tag"] and left["exit_reason"] == right["exit_reason"])
        require(left["open_timestamp"] == right["open_timestamp"] and left["close_timestamp"] == right["close_timestamp"])
        require(abs(left["profit_abs"] - right["profit_abs"]) < 1e-7)
    print(json.dumps({"verified": True, "basis": "historical_public_wall_proxy", **a}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
