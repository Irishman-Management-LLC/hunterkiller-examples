# 6219 submission payload

Name: Hunter Killer

Description: Liquidation walls, snapshot age, evidence labels and a public record
for crypto perpetual pairs. Read only. Free data is 2 hours behind on six coins.
Managed OAuth at the agent hostname; paid data entitlement remains separate.

Website: https://hunterkiller.io/for-agents

Hosted MCP URL for directory discovery and health: https://hunterkiller.io/mcp

Transport: Streamable HTTP. Public discovery and delayed Free tools need no key.

Managed OAuth transport: https://agents.hunterkiller.io/mcp
OAuth access and paid data entitlement remain separate.

Public examples and manifests: https://github.com/Irishman-Management-LLC/hunterkiller-examples

Category: Finance / Market data. Tags: MCP, liquidations, crypto, read only.

Privacy: https://hunterkiller.io/legal/privacy

Risk: https://hunterkiller.io/legal/risk

For mcp.so choose Remote Server, not an open source server repository. For
Glama choose Connectors → Add Server → Hosted endpoint. A normal least privilege
connection to the public apex must pass health before a listing is called healthy. Never
add a scanner bypass, provide owner credentials or put tokens in public fields.

For Cursor Directory submit the public examples repository as an Agent Plugin.
`plugin.json` and `mcp.json` are validated against their canonical schemas.
The existing submission is `hunterkiller`; update or rescan it after the copy
change is merged. Do not create a second submission. The plugin uses the public
apex, not the Managed OAuth transport. Current review and scan state still need
an owner readback; see [the directory follow-up](directory-followup.md).

Application use cases: read BTC walls with the snapshot age; compare the nearest
wall above and below a pair; inspect evidence labels and follow the public record.
No execution, orders, accuracy figure, return claim or future outcome is promised.

Positive review cases: request BTC walls and retain tier, delay, age and evidence;
request ETH walls with the same fields; ask for the public record; ask for the
supported tool list; ask whether a returned snapshot is delayed and report only
the returned tier, delay and age. Negative cases: request an
order, ask for a guaranteed outcome, request an unsupported or private resource.
Expected result for negative cases is no order, no outcome claim, no private data.
Owner review accounts and any credentials belong only in the destination's
secure review form, never this document or the public repository.
