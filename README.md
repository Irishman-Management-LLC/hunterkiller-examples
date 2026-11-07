# Hunter Killer agent examples

```sh
curl --fail-with-body --max-time 20 https://hunterkiller.io/api/v1/levels/BTCUSDT
# Or, with only Python's standard library:
python3 examples/one_call.py BTCUSDT
```

The keyless rollout and wrapper publication are pending a live receipt. A first
call can still return 401. A failure is never labeled as successful data. No
external paying use is claimed.

Read liquidation walls, snapshot age, evidence labels and a public record.
The strategy examples use paper orders. Live execution is disabled.
Descriptive measurements, not trading advice.

Free data is 2 hours behind on six coins. Inspect `tier`, `delay_sec`,
`as_of_iso`, `age_sec`, `nearest`, `walls`, `truth` and `record`. Keep these
fields with any result you show. An empty ladder is not a trading instruction.
Calls can return 401, 403, 402, 429 or 503; errors must reach the caller.
Internal verification must use `python3 examples/one_call.py --probe` so probes
are not confused with external adoption.

## Integrations

* `packages/langchain`: `hunterkiller-langchain`, Python transport and LangChain factory.
* `packages/crewai`: `hunterkiller-crewai`, CrewAI factory using the same transport.
* `packages/composio`: `hunterkiller-composio`, experimental standalone session tool.
* `packages/npm`: `hunterkiller-agent-tools`, Node client, LangChain factory and function definitions.
* `schemas/openai-function.json`: strict Responses API function schema. Dispatch to the read only HTTP client.
* `schemas/composio-openapi.json`: public REST definition for custom bindings, not a hosted catalog listing.
* `space`: manual Gradio ladder demo for Hugging Face Spaces.
* `examples/sdk.py` and `examples/sdk.mjs`: existing published SDK Desk Read examples.
* [`examples/freqtrade`](examples/freqtrade/README.md): the Freqtrade paper strategy, native historical public wall proxy table and API key signup link.
* [`examples/hummingbot`](examples/hummingbot/README.md): the Hummingbot paper grid and its labeled historical quote model table.
* [`strategies`](strategies/README.md): shared point in time inputs, sealed observations, [full results](strategies/RESULTS.md), costs and losses.

The wrappers call the public endpoint directly because the versions of the
existing SDKs currently on PyPI and npm do not expose `levels`. They do not
compute walls or grades. Credentials, if supplied by the application, never
appear in the model's argument schema. No payment is automatic.

## MCP

`https://hunterkiller.io/mcp` is the public door. Discovery, `list_symbols`
and `hk_levels` need no key for the six Free coins, 2 hours behind. REST and
these two tools share 60 requests per minute and 500 per UTC day per IP.
Response headers state the actual limit and quota mode. Directory health
checks that do not authenticate use this public apex URL.

`https://agents.hunterkiller.io/mcp` is the Managed OAuth transport for live
tools. Complete its normal sign in flow in your MCP client. OAuth transport
access and paid Hunter Killer data entitlement are separate. The protected
apex twin `/mcp/protected` retains the same gate. `registry/server.json`
version 1.0.1 lists the public apex first and the OAuth remote second; it
is hosted metadata, not an installable open source server implementation.

## Public source and risk

[Agent door](https://hunterkiller.io/for-agents), [proof](https://hunterkiller.io/proof),
[privacy](https://hunterkiller.io/legal/privacy), [risk](https://hunterkiller.io/legal/risk).
Never infer a future return or trade recommendation from these measurements.
The paper examples retain their historical proxy inputs, costs and losing
periods. Those results describe a simulation, not live performance.
