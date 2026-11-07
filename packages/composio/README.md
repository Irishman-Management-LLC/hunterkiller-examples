# Hunter Killer for Composio

```sh
pip install hunterkiller-composio==0.1.0
```

```python
from composio import Composio
from hunterkiller_composio import create_levels_tool
client = Composio()  # Your application's Composio account configuration
session = client.create(user_id="your-user", experimental={
    "custom_tools": [create_levels_tool(client)]
})
print(session.execute("LOCAL_HUNTERKILLER_LEVELS", {"symbol": "BTCUSDT"}))
```

This is an in-process standalone tool using Composio's experimental custom tool
API. It is not a hosted listing in Composio's catalog. Composio account access is
needed for its session; the delayed Hunter Killer call needs no paid key after
the keyless release. Free data is 2 hours behind on six coins. The transport
returns source fields unchanged and raises on HTTP failure. No orders or estimates.
The packages and keyless endpoint must be released before this example works.

[Composio custom tools](https://docs.composio.dev/docs/extending-sessions/custom-tools-and-toolkits).
