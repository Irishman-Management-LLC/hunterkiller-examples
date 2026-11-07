#!/bin/sh
set -eu
data=/repo/strategies/data/20261105-20261107
python /repo/strategies/run_freqtrade_backtest.py "$data" /tmp/hk-native-result >&2
python /repo/strategies/verify_backtest_results.py "$data" /tmp/hk-native-result/complete-result.json >&2
# Stdout is only the fresh result archive. No host write mount is required.
tar -C /tmp/hk-native-result -cf - .
