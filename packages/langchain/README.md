# Hunter Killer for LangChain

Read liquidation walls with the snapshot age and the source record intact.
Free data is 2 hours behind on six coins. This tool never places an order.

```sh
pip install 'hunterkiller-langchain[langchain]==0.1.0'
```

```python
from hunterkiller_langchain import create_levels_tool
print(create_levels_tool().invoke({"symbol": "BTCUSDT"}))
```

For a paid key, pass `key=...` to the factory in your application. Keys never
appear in the model tool schema. Calls time out after 15 seconds, do not retry,
and raise on HTTP errors, including 401, 402 and 429. No cached or invented
ladder replaces a failure. Read `tier`, `delay_sec`, `as_of_iso`, `age_sec`,
`truth` and `record` before using any value. This is descriptive data, not advice.

The installation command requires the package to have been published. Check
the repository rollout status before running the keyless example.

[Tool API](https://docs.langchain.com/oss/python/langchain/tools)
and [public data door](https://hunterkiller.io/for-agents).
