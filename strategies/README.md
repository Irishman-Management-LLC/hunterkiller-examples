# Walls in paper strategies

Start with one real data call:

```sh
curl --fail-with-body --max-time 20 https://hunterkiller.io/api/v1/levels/BTCUSDT
```

Free data is 2 hours behind on six coins. The keyless rollout is pending a live
receipt. A 401 or an empty response is not a successful first call. A supplied
key can read live data according to its entitlement and can consume credits.
Neither example makes a payment or falls back to a different access path.

These are paper spot examples for BTC/USDT. They consume the API's `nearest`
pair. They do not calculate walls, score their accuracy or promise a return.
The lower wall is the stop and the upper wall is the target for a long example.
An entry requires both walls, a price between them and at least as much room to
the target as to the stop. This fixed teaching rule has not been optimized.
Losses, fees and stale data matter. A stop is an instruction, not a fill guarantee.

## Freqtrade 2026.10

Install the transport without any model framework dependency, then copy both
files to the framework's strategy directory:

```sh
python -m pip install ./packages/langchain
cp strategies/hk_strategy_core.py strategies/HunterKillerWalls.py user_data/strategies/
```

Configure `dry_run: true`, one open trade, spot mode, `BTC/USDT` as the static
pair list, and a bounded stake. `HunterKillerWalls` rejects `dry_run: false`.
It uses 5 minute candles, a frozen wall pair in the entry tag and a maximum
24 hour holding period. The framework manages the stop. The target is checked
at the framework's callback price, rather than assuming a wick touch filled it.
New API data never moves an existing trade's exit walls.

The optional `hk_levels.key` config value is application supplied. Keep it out
of commits and logs. No environment key is discovered automatically. Omit it
for Free. `hk_levels.probe: true` marks internal verification only.

Historical mode requires an explicit `hk_levels.replay` JSONL path. It never
calls the live API. Use the framework's `backtesting` command with a fixed
timerange, declared fees, `--cache none` and `--export trades`. Record the exact
framework version and retain its full trades file, including losing trades.
Run Freqtrade's lookahead analysis before drawing conclusions from a backtest.

## Hummingbot 2.17

Install the same transport in the Hummingbot environment. Copy
`hk_strategy_core.py` and `hk_wall_grid.py` into its `scripts/` directory, then
create a V2 config for `hk_wall_grid`. The only allowed connector is
`binance_paper_trade` and the only pair is `BTC-USDT`.

The V2 script starts with no example inventory. Its bids and asks sit inside
the frozen wall pair. It makes at most two quotes per side, refreshes every
30 seconds and budgets at most 100 USDT by default, including held inventory.
It never sells more example inventory than its own fills added. The framework
checks available balances and exchange rounding before orders are submitted.
After a wall break or an unavailable feed, it cancels its quotes and closes its
own paper inventory. Exchange minimum size can leave dust. Other orders and
initial balances are not counted as this example's inventory.
The stop intent remains set while cancellations finish, even if price moves
back inside the walls. Base fees are deducted from example inventory. A paper
position also closes after 24 hours. Start in a fresh paper session; this script
does not restore its inventory ledger after a restart.

`api_key` is an optional secret config field, omitted for Free. A running
script polls at most once a minute in a background thread with a 15 second HTTP
timeout. Importing the script makes no request. Paper fills are simulated.

## Point in time data and results

Exact capture format:

```json
{"received_at": 1794000000.0, "payload": {"ok": true, "symbol": "BTCUSDT", "as_of": 1793992800, "tier": "delayed", "delay_sec": 7200, "mark": {"price": 100}, "nearest": {"below": null, "above": null}}}
```

The numbers in that format example are synthetic, not a market observation.
The complete API payload, including `truth`, `record` and evidence labels,
is retained by the collector. `received_at` is HTTP completion time; `as_of`
remains the source's snapshot time. The replay does a backward lookup only.
It rejects unsorted or duplicate receipts, never reads a future snapshot and
does not carry a receipt beyond 15 minutes. A failed receipt interrupts the
last success. A snapshot more than 30 minutes older than its stated delay
cannot create a new entry. These limits are fixed before examining results.

`collect_levels.py OUTPUT --count 1` makes one manual call. Larger counts are
finite, at one call per minute. It exclusively creates the requested output.
Use `--probe` for internal checks. `--authenticated` explicitly opts into the
application's `HK_LEVELS_API_KEY` environment value; otherwise it is ignored.
No collector, bot, service or schedule is installed or started by these files.

A real historical results table is pending an approved dated dataset and
qualified replay. No PnL, hit rate or live trading result is claimed here.
Do not substitute today's walls for historical inputs or select only reached
walls. Retain every eligible candle, skipped interval, cost assumption and loss.

`grid_replay.py` is an offline OHLCV model of the shared grid quotes, not a
native Hummingbot backtest. It accepts exact receipt JSONL and contiguous real
5 minute candle CSV (`timestamp,open,high,low,close`, UTC open in seconds):

```sh
python strategies/grid_replay.py receipts.jsonl candles.csv result.json --source-url ACTUAL_CANDLE_SOURCE_URL
```

The model keeps every fill and loss. It starts with 1000 USDT of simulated cash,
uses a 100 USDT notional grid budget, charges an assumed 0.1 percent on each
side and adds 0.05 percent slippage to market exits. Those are declared model
costs, not an account's observed fee tier. A quote needs a cross, not a touch.
Ambiguous bars take the losing boundary first. New orders wait for the next
candle. It refreshes once per 5 minute bar, unlike the script's 30 second loop.
It cannot reconstruct queue position, depth, latency or partial fills from
OHLCV. It closes remaining inventory at the end and retains input hashes and
coverage gaps. Its result must keep that model label and those limitations.

## Check the example contracts

```sh
python -m unittest discover -s strategies/tests -p 'test_*.py' -v
```

These hermetic tests use explicitly synthetic fixtures. They establish input
and timing behavior, not market performance or a successful live API call.

Official framework references:
[Freqtrade strategies](https://www.freqtrade.io/en/stable/strategy-customization/),
[Freqtrade backtesting](https://www.freqtrade.io/en/stable/backtesting/),
[Hummingbot V2 scripts](https://hummingbot.org/strategies/scripts/).
