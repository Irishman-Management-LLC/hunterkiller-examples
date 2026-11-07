"""Fable6219: directory probes use public apex; registered OAuth door remains."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def test_registry_1_0_1_lists_public_apex_first_and_keeps_oauth():
    manifest = json.loads((ROOT / "registry/server.json").read_text())
    assert manifest["version"] == "1.0.1"
    assert manifest["name"] == "io.github.Irishman-Management-LLC/hunterkiller"
    assert manifest["remotes"] == [{"type": "streamable-http", "url": url} for url in (
        "https://hunterkiller.io/mcp", "https://agents.hunterkiller.io/mcp")]
    assert "packages" not in manifest

def test_cursor_plugin_uses_unauthenticated_health_door():
    config = json.loads((ROOT / "mcp.json").read_text())
    assert config["mcpServers"]["hunterkiller"] == {
        "type": "streamable-http", "url": "https://hunterkiller.io/mcp"}
