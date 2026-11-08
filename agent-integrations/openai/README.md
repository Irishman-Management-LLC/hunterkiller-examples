# OpenAI review package for the public apex

Fable rulings m-1794097680273-823c and m-1794098558037-1d00, card 6238b. The existing OpenAI draft's server
URL was locked to the original uploaded package. This replacement declares the
public apex with Authentication None. No login or reviewer credential is needed
for the Free door. Paid tools still enforce the existing entitlement.

Package: [hunterkiller-openai-app.zip](hunterkiller-openai-app.zip)

SHA256: `74622407d897c48f10551b15c721d93b7578264c218b4c36b2e702dbf6edb92f`

Size: 6808 bytes.

The ZIP contains root `plugin.json`, `mcp.json`, `LICENSE` and `assets/icon.png`.
The unpacked [package](package/) is included for review. The MCP URL is
`https://hunterkiller.io/mcp`; its OpenAI authentication declaration is exactly
`{"type": "none"}`, without an OAuth block or request headers.

The five positive and three negative cases remain identical to the approved
original. The demo URL is explicitly included under
`extensions.com.openai.review.demo_recording_url`:
https://hunterkiller.io/assets/openai-demo.mp4 . The description, long description and release notes now state the public
endpoint and no key needed exactly as ruled in1d00. The complete review object,
including commerce_description, and all other original fields remain unchanged. The icon and license are byte
identical. The challenge path remains `/.well-known/openai-apps-challenge`;
this package does not change its hosted contents.

Before packaging, marked anonymous initialize and tools/list requests to the
public apex returned 200. All 18 tool titles, descriptions and annotation objects
match the approved metadata now live in release 149. Receipts and actual public
responses are retained in [evidence](evidence/). [receipt.json](receipt.json)
records package hashes and the allowed field comparison with the original ZIP.

The [official OpenAI packaging reference](https://developers.openai.com/plugins/build/plugins#configure-mcp-authentication)
places Authentication None under each server's `extensions.com.openai.auth`.
The [submission reference](https://developers.openai.com/plugins/deploy/submission#configure-onboarding-review-and-publication)
defines the walkthrough field. Reviewer instructions stay outside the ZIP.

## Owner readback

Upload the ZIP through the existing owner's OpenAI draft workflow. Check the
retained MCP settings show the public apex and Authentication None, then rescan.
Keep the eight review cases and walkthrough URL. Reviewer instructions:

> No login is needed. Connect to https://hunterkiller.io/mcp. Free liquidation data covers six coins, 2 hours behind. Keep the returned tier, delay and snapshot age. Paid tools require the existing data entitlement and return an entitlement message when it is absent.

Retain the saved endpoint, authentication, scan result and final OpenAI
submission confirmation. This source package and a successful download are
preparation receipts; no upload, review acceptance or publication is claimed.

## Validation scope

The plugin manifest passes the portable version 1.0.0 schema. The generic MCP
version 1.0.0 schema accepts the original base connection fields but does not
define server vendor extensions, so it rejects the documented OpenAI auth
object. The exact diagnostic is retained in
[evidence/portable-schema-diagnostic.json](evidence/portable-schema-diagnostic.json);
no full portable MCP schema pass is claimed. This package follows OpenAI's
explicit authentication declaration at the reference above. ZIP CRC, exact
archive members, unpacked byte identity, unchanged cases and other original fields,
asset paths and PNG dimensions are verified. Final portal import and saved
Authentication None remain owner readbacks.
