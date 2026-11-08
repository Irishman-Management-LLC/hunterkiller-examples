# OpenAI review package for the public apex

This updates the existing Hunter Killer OpenAI package to **0.1.1**. Its server is
`https://hunterkiller.io/mcp`, with Authentication None. No OAuth configuration,
request headers or reviewer credentials are included. The separate Managed OAuth
service at `agents.hunterkiller.io` is unchanged.

Package: [hunterkiller-openai-app.zip](hunterkiller-openai-app.zip).
The exact size, SHA256, baseline provenance and preservation hashes are in
[receipt.json](receipt.json). The ZIP contains root `plugin.json`, `mcp.json`,
`LICENSE` and `assets/icon.png`; [package](package/) retains their exact bytes.

The description, long description and release notes state:

> No login is required. The public endpoint serves discovery and the six Free coins two hours behind without credentials. Paid tools answer with an entitlement message instead of data.

The publisher, icon, license, privacy and risk links, five positive cases, three
negative cases, and demo URL remain unchanged. The demo is
https://hunterkiller.io/assets/openai-demo.mp4 . Commerce disclosure retains the
human Stripe Checkout step and states that payment and trading are not automatic.
The package version is separate from registry version 1.0.2 and observed MCP
server version 1.3.0. The challenge path remains `/.well-known/openai-apps-challenge`;
this package does not change its hosted contents.

## Owner readback

Replace the package in the existing owner's OpenAI draft. Verify the retained MCP
URL and Authentication None, then rescan. Preserve the eight review cases and
walkthrough URL. Copy this exact text into the portal's reviewer instructions:

> No login is required. The public endpoint serves discovery and the six Free coins two hours behind without credentials. Paid tools answer with an entitlement message instead of data.

Reviewer instructions are a separate portal field; this package does not invent
an unsupported manifest field. The same public access text is in the package's
description, long description and release notes so the ZIP conveys this context.
Retain the saved endpoint, authentication, scan result and final submission
confirmation. No portal upload, saved instruction change, review acceptance,
submission or publication is claimed by this source package.

## Validation and reproduction

Run `python3 agent-integrations/openai/build_package.py` from the repository root
to reproduce the ZIP using fixed timestamps, permissions and member order. Run
the same command with `--check` to verify the retained ZIP, CRC and receipt hashes.
The receipt must be refreshed whenever package source changes.

The plugin manifest passes the portable version 1.0.0 schema. The generic MCP
version 1.0.0 schema rejects server vendor extensions, including OpenAI's auth
object; the base connection fields pass when that extension is removed only for
the diagnostic. No full vanilla MCP schema pass is claimed. The retained
[diagnostic](evidence/portable-schema-diagnostic.json) documents that limitation.
The actual package retains OpenAI's documented `extensions.com.openai.auth`
declaration with exactly `{"type":"none"}`.

[Current public checks](evidence/public-review-20261108/) record anonymous
initialize HTTP 200, initialized HTTP 202, tools/list HTTP 200 with 18 tools and
a successful Free BTC read with `delay_sec: 7200`; demo HEAD returned HTTP 200
and `video/mp4`. These are dated observations, separate from portal import.
Archive CRC, source identity, deterministic reproduction, retained fields and
the 192 by 192 PNG are verified.

References: [OpenAI authentication](https://developers.openai.com/plugins/build/plugins#configure-mcp-authentication)
and [submission](https://developers.openai.com/plugins/deploy/submission#configure-onboarding-review-and-publication).
