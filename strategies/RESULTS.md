# Historical public wall proxy: November 5 and 6, 2026

Both examples lost money in this fixed window. These are historical public wall
proxy results, not an API replay or live performance. The window and rules were
fixed before results were read. There was no parameter search.

Inputs are BTC/USDT spot candles from Bybit and walls actually served to public
Free readers in the 1 hour view. The ledger did not retain original snapshot
time, delay or the API nearest fields. The public pair was reconstructed with
the unchanged serving selector. Unknown age remains unknown. No owner data or
unpublished computed peaks enter the inputs.

| Model | Net result, USDT | Recorded activity | Losing activity |
| --- | ---: | --- | --- |
| Native Freqtrade 2026.10 | -4.38 | 5 closed positions | All 5 positions |
| Grid quote model for the paper script | -1.79 | 25 fill events | 6 sell fills |

Each model started with 1000 USDT of simulated cash and a 100 USDT stake or
notional budget. Fill events and closed positions are different units. The
grid model is an offline OHLCV replay of the shared quote logic, not a native
Hummingbot backtest. The script itself is checked against Hummingbot 2.17.

| UTC day | Native Freqtrade realized result, USDT | Grid equity change, USDT |
| --- | ---: | ---: |
| November 5 | -4.01 | -0.99 |
| November 6 | -0.38 | -0.80 |
| Whole window | -4.38 | -1.79 |

Native daily values group closed positions by UTC exit date. Grid daily values
mark open inventory at the candle close; the final day includes closing costs.
Displayed daily values may differ from the rounded total by 0.01 USDT.

## Costs and limits

Native Freqtrade charges 0.15 percent per side: an assumed 0.10 percent fee plus
a 0.05 percent adverse execution allowance. The allowance is encoded as a fee,
not a simulated change to the fill price. The grid charges 0.10 percent on each
fill and 0.05 percent slippage on market closes. These are declared assumptions,
not an account's observed fees or executions. Both examples use spot, one times
leverage, with no funding or borrowed inventory.

There are 576 closed 5 minute candles, plus one native startup candle. The
publication export contains 3829 public receipts and 470 ambiguous or unavailable
receipts represented as gaps. An input is available on 509 of 576 candle closes;
the other 67 are missing or stale. Available input does not imply a valid entry.
No old receipt is carried more than 15 minutes. A 1 second availability buffer
covers the ledger's floored timestamps.

OHLCV does not establish queue position, depth, latency or partial fills. The
grid requires a price cross, credits one side per bar with buys first, and takes
the losing boundary first when a bar is ambiguous. Its 5 minute refresh differs
from the script's 30 second refresh. Native Freqtrade uses its own candle and
stop rules and closes its final position at 23:55 UTC on November 6; the grid's
final close uses the last candle's close. Captured instrument constraints are
dated November 7, rather than a historical reconstruction of exchange rules.

This is a small integration example. It does not establish a trading advantage.

## Full records and reproduction

The [sealed inputs](data/20261105-20261107/dataset.manifest.json) include hashes
and the actual [candle request receipt](data/20261105-20261107/candles.receipt.json).
All [native positions](data/20261105-20261107/results/freqtrade.complete.json)
and [grid fills](data/20261105-20261107/results/grid.complete.json) are retained,
including every loss. Input coverage and missing timestamps are visible in the
[public publication proxy](data/20261105-20261107/public-wall-proxy.jsonl).

From the repository root, reproduce the complete native result without network
or a writable host mount:

```sh
docker run --rm --network none --read-only --cap-drop ALL \
  --pids-limit 128 --memory 2g --cpus 2 --tmpfs /tmp:rw,size=256m \
  -e PYTHONDONTWRITEBYTECODE=1 -e OPENBLAS_NUM_THREADS=1 \
  -e FT_APP_ENV=offline-backtest \
  -v "$PWD:/repo:ro" -w /repo/strategies \
  --entrypoint /bin/sh \
  freqtradeorg/freqtrade@sha256:956c03780934eeb93734a1f352e7e150b73becdafa3767a947a25ad2422fba2e \
  /repo/strategies/reproduce_freqtrade.sh > native-public-wall-proxy.tar
```

The pinned image is Linux amd64. `FT_APP_ENV=offline-backtest` sets the offline
embedding context and avoids the framework's Docker convenience chown. Network remains disabled and
the source remains read only. CCXT parses the captured public instrument
response; the native trading engine and all price inputs are unchanged.

`python -m unittest discover -s strategies/tests -p 'test_*.py'` verifies the
input hashes, every entry's prior public wall receipt, cash reconciliation and
the complete grid replay. The native CI job reruns Freqtrade from these inputs
and retains its fresh archive. There is no skip for a losing result.

An exact API input capture began November 7. Its first response was 401, retained
as a gap. A second table is due no earlier than November 21 after two weeks,
with outages and coverage disclosed. Internal probe calls are not adoption.
