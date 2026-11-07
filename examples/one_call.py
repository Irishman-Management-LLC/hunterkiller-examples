"""One real HTTP call; --probe marks internal verification, never customer use."""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "packages/langchain"))
from hunterkiller_langchain import get_levels

if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("symbol", nargs="?", default="BTCUSDT")
    p.add_argument("--probe", action="store_true")
    args = p.parse_args()
    print(json.dumps(get_levels(args.symbol, probe=args.probe), indent=2))
