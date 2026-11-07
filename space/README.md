---
title: Hunter Killer walls
emoji: 🧱
colorFrom: gray
colorTo: yellow
sdk: gradio
sdk_version: 6.31.0
python_version: "3.12"
app_file: app.py
pinned: false
license: mit
short_description: Liquidation walls, snapshot age, evidence and public record.
---

One button reads BTC liquidation walls from Hunter Killer. The free snapshot is
2 hours behind. Snapshot age and evidence labels accompany the ladder. There
are no background calls, orders, keys or paid generation. A failed request
shows an error instead of made up levels. No secrets or API key are required.
For owner verification, set the optional Space variable `HK_INTERNAL_PROBE=1`;
those requests carry the internal probe header and must not count as adoption.
Unset that variable for genuine public use after the keyless API live receipt.
Until then this is staging, not a successful public demo.
