"""Offline OpenAI package review contract and preserved artifact checks."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "agent-integrations/openai"
PUBLIC_TEXT = (
    "No login is required. The public endpoint serves discovery and the six Free "
    "coins two hours behind without credentials. Paid tools answer with an "
    "entitlement message instead of data."
)


def test_openai_archive_and_public_access_contract():
    subprocess.run([sys.executable, str(PACKAGE / "build_package.py"), "--check"], check=True)
    with zipfile.ZipFile(PACKAGE / "hunterkiller-openai-app.zip") as archive:
        for name in archive.namelist():
            assert archive.read(name) == (PACKAGE / "package" / name).read_bytes()
        plugin = json.loads(archive.read("plugin.json"))
        mcp = json.loads(archive.read("mcp.json"))
    assert plugin["version"] == "0.1.1"
    assert mcp["mcpServers"]["hunterkiller"] == {
        "type": "streamable-http", "url": "https://hunterkiller.io/mcp",
        "extensions": {"com.openai": {"auth": {"type": "none"}}},
    }
    openai = plugin["extensions"]["com.openai"]
    assert PUBLIC_TEXT in plugin["description"]
    assert len(openai["interface"]["shortDescription"]) <= 30
    assert PUBLIC_TEXT in openai["interface"]["longDescription"]
    assert PUBLIC_TEXT in openai["publication"]["release_notes"]
    assert PUBLIC_TEXT in (PACKAGE / "README.md").read_text()
    assert openai["review"]["demo_recording_url"] == "https://hunterkiller.io/assets/openai-demo.mp4"
    cases = openai["review"]["test_cases"]
    assert [len(cases[key]) for key in ("positive", "negative")] == [5, 3]
    canonical = json.dumps(cases, sort_keys=True, separators=(",", ":")).encode()
    assert hashlib.sha256(canonical).hexdigest() == "43a521a6db0f544e7d469a0cfa7e4ed1529505cffab3ddfef909e3ea6f94e1a8"
    receipt = json.loads((PACKAGE / "receipt.json").read_text())
    for name in ("mcp.json", "LICENSE", "assets/icon.png"):
        assert receipt["member_sha256"][name] == receipt["baseline"]["member_sha256"][name]
