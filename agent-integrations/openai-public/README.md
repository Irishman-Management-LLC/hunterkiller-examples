# New public OpenAI app package

[Download hunterkiller-public.zip](hunterkiller-public.zip) for a **NEW app**:
choose **Upload new plugin / With MCP**. Do **not** choose Upload new version on
an existing app. Do not replace or update the existing Managed OAuth app.
No OpenAI portal creation, upload, saved settings or submission is performed by
this repository change.

The portable identity is `hunterkiller-public`; its display name remains
**Hunter Killer** and package version remains **0.1.1**. This is a distinct app
identity derived from the existing public package at immutable commit
`9e4aa75d3629187d3b312431cef06c2a9734ab05`. Only `plugin.json.name` changes.
No app ID, `apps/` directory, `.app.json` file or update binding is included.
The MCP alias remains `hunterkiller` and its configuration is byte-identical:
`https://hunterkiller.io/mcp`, Authentication None, with no OAuth configuration
or request headers.

The publisher, complete listing text, icon, privacy/terms/risk links, all five
positive and three negative cases, and demo URL are preserved. The existing
`../openai/` package and ZIP remain unchanged. The separate Managed OAuth
service at `agents.hunterkiller.io` is unchanged.

Copy this exact text into the new app's reviewer instructions:

> No login is required. The public endpoint serves discovery and the six Free coins two hours behind without credentials. Paid tools answer with an entitlement message instead of data.

The same text remains in the ZIP's description, long description and release
notes. Reviewer instructions are a separate portal field; no unsupported
manifest instruction field is invented. After a future owner upload, verify the
retained public endpoint and Authentication None in the **new app** before
scanning or submitting. No old app should be selected for an update.

Run `python3 agent-integrations/openai-public/build_package.py` to reproduce
the ZIP, or append `--check` to verify deterministic bytes, CRC and receipt.
[receipt.json](receipt.json) records the archive SHA256 and preservation scope.
The plugin manifest passes the portable schema. The generic MCP schema rejects
OpenAI's documented auth vendor extension; its base connection fields pass
without that extension for diagnostics only. No full vanilla MCP schema pass
is claimed. [Existing dated public checks](../openai/evidence/public-review-20261108/)
apply to the identical endpoint configuration; no duplicate live calls are needed.

Reference: [OpenAI submission](https://developers.openai.com/plugins/deploy/submission).
