"""Capture finite, exact API receipts. A failed request is a gap, never data."""
import argparse
import json
import os
from pathlib import Path
import time

from hk_strategy_core import LevelsFeed


def bounded_count(value):
    count = int(value)
    if not 1 <= count <= 20161:
        raise argparse.ArgumentTypeError("count must be between 1 and 20161")
    return count


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path)
    parser.add_argument("--count", type=bounded_count, default=1)
    parser.add_argument("--probe", action="store_true", help="Mark internal checks, never real adoption")
    parser.add_argument("--authenticated", action="store_true", help="Explicitly use HK_LEVELS_API_KEY; may spend credits")
    args = parser.parse_args()
    key = os.environ["HK_LEVELS_API_KEY"] if args.authenticated else None
    feed = LevelsFeed(key=key, probe=args.probe)
    all_ok = True
    started = time.time()
    status = {"started_at": started, "target_attempts": args.count, "attempts": 0,
              "successes": 0, "errors": 0, "first_valid_receipt_at": None,
              "probe": args.probe, "complete": False}
    status_path = args.output.with_suffix(".status.json")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    # Exclusive create prevents accidentally splicing overlapping capture windows.
    with args.output.open("x") as stream:
        for index in range(args.count):
            previous = feed.timeline.times[-1] if feed.timeline.times else None
            feed.poll(time.time())
            received_at = feed.timeline.times[-1]
            if previous is not None and received_at <= previous:
                raise RuntimeError("Clock did not advance; capture stopped without inventing a timestamp")
            sample = feed.timeline.samples[-1]
            row = {"received_at": received_at, "probe": args.probe}
            if sample is None:
                row["error"] = feed.last_error
                all_ok = False
                status["errors"] += 1
            else:
                row["payload"] = sample.payload
                status["successes"] += 1
                if status["first_valid_receipt_at"] is None:
                    status["first_valid_receipt_at"] = received_at
            stream.write(json.dumps(row, allow_nan=False) + "\n")
            stream.flush()
            status.update(attempts=index + 1, last_received_at=received_at, complete=index + 1 == args.count)
            temporary = status_path.with_suffix(".tmp")
            temporary.write_text(json.dumps(status, indent=2) + "\n")
            temporary.replace(status_path)
            if index + 1 < args.count:
                time.sleep(max(0, feed.next_poll - time.time()) + 0.01)
    return 0 if all_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
