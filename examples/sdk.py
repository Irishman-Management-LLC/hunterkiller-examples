"""Existing published SDK example; no model call and no paid key required."""
import json
from hunterkiller import desk_read

if __name__ == "__main__":
    print(json.dumps(desk_read("BTCUSDT"), indent=2))
