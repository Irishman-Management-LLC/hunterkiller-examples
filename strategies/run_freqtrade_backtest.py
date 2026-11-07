"""Native Freqtrade replay using captured public candles and instrument metadata.

Run in the pinned official image with networking disabled. The exchange object
is injected with the actual captured public instrument, not fabricated prices
or a mock trading engine. Costs are explicit assumptions, not an account fee.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("data", type=Path, help="Directory with bybit/BTC_USDT-5m.json, proxy and instrument.raw.json")
    parser.add_argument("output", type=Path)
    parser.add_argument("--timerange", default="20261105-20261107")
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    user_data = args.output / "user_data"
    user_data.mkdir()

    from freqtrade.configuration import Configuration
    from freqtrade.enums import RunMode
    from freqtrade.resolvers import ExchangeResolver
    from freqtrade.optimize.backtesting import Backtesting

    settings = {
        "dry_run": True, "dry_run_wallet": 1000, "stake_currency": "USDT", "stake_amount": 100,
        "max_open_trades": 1, "tradable_balance_ratio": 1, "fiat_display_currency": "USD",
        "timeframe": "5m", "strategy": "HunterKillerWalls",
        "strategy_path": str(Path(__file__).resolve().parents[1] / "examples/freqtrade"),
        "user_data_dir": str(user_data), "datadir": str(args.data / "bybit"), "dataformat_ohlcv": "json",
        "trading_mode": "spot", "margin_mode": "", "timerange": args.timerange,
        "exchange": {"name": "bybit", "key": "", "secret": "", "enable_ws": False,
                     "ccxt_config": {"enableRateLimit": True},
                     "pair_whitelist": ["BTC/USDT"], "pair_blacklist": []},
        "pairlists": [{"method": "StaticPairList"}],
        "entry_pricing": {"price_side": "other", "use_order_book": False},
        "exit_pricing": {"price_side": "other", "use_order_book": False},
        "unfilledtimeout": {"entry": 10, "exit": 10, "unit": "minutes"},
        # 0.10 percent fee plus a 0.05 percent adverse-execution allowance per
        # side. Freqtrade represents this allowance as a fee, not a price shift.
        "fee": 0.0015, "backtest_cache": "none", "export": "trades",
        "exportdirectory": str(args.output),
        "hk_levels": {"replay": str(args.data / "public-wall-proxy.jsonl"), "public_wall_proxy": True},
    }
    config_path = args.output / "config.json"
    config_path.write_text(json.dumps(settings, indent=2) + "\n")
    config = Configuration({"config": [str(config_path)], "datadir": str(args.data / "bybit")}, RunMode.BACKTEST).get_config()
    exchange = ExchangeResolver.load_exchange(config, validate=False, load_leverage_tiers=False)
    raw = json.loads((args.data / "instrument.raw.json").read_text())
    if raw.get("retCode") != 0 or raw.get("result", {}).get("category") != "spot":
        raise ValueError("Expected a successful captured public spot instrument")
    instruments = raw["result"]["list"]
    if len(instruments) != 1 or instruments[0].get("symbol") != "BTCUSDT":
        raise ValueError("Expected exactly the captured BTCUSDT instrument")
    # Bybit's CCXT parser lives inside fetch_spot_markets, rather than
    # parse_market. Replay only its captured public HTTP response; the parser,
    # instrument rules and the complete Freqtrade backtest engine stay native.
    api = exchange._api
    original_read = api.publicGetV5MarketInstrumentsInfo
    def captured_public_instruments(request):
        if request != {"category": "spot"}:
            raise ValueError("Unexpected offline metadata request")
        return raw
    api.publicGetV5MarketInstrumentsInfo = captured_public_instruments
    try:
        markets = api.fetch_spot_markets({})
    finally:
        api.publicGetV5MarketInstrumentsInfo = original_read
    if len(markets) != 1:
        raise ValueError("Expected one parsed captured instrument")
    market = markets[0]
    if market["symbol"] != "BTC/USDT" or not market["spot"]:
        raise ValueError("Captured instrument is not BTC/USDT spot")
    exchange._markets = {market["symbol"]: market}
    exchange._api.set_markets([market])
    exchange._api_async.set_markets([market])
    try:
        backtest = Backtesting(config, exchange=exchange)
        backtest.start()
        result = backtest.results
        result["hk_provenance"] = {
            "input_basis": "historical_public_wall_proxy_not_api_replay_not_live_performance",
            "engine": "Freqtrade 2026.10", "timerange": args.timerange,
            "fee_each_side": 0.001, "adverse_execution_allowance_each_side": 0.0005,
            "cost_encoding": "Combined fee 0.0015 per side, not an explicit fill-price slippage model",
            "instrument_constraints": "Captured public instrument metadata, dated in instrument.receipt.json",
            "input_sha256": {name: hashlib.sha256((args.data / name).read_bytes()).hexdigest()
                             for name in ["bybit/BTC_USDT-5m.json", "public-wall-proxy.jsonl", "instrument.raw.json"]},
        }
        (args.output / "complete-result.json").write_text(json.dumps(result, indent=2, default=str) + "\n")
        return 0
    finally:
        exchange.close()


if __name__ == "__main__":
    raise SystemExit(main())
