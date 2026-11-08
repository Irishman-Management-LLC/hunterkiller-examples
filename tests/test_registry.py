"""The official registry exposes only the public, unauthenticated MCP door."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def test_registry_1_0_2_lists_only_public_apex():
    manifest = json.loads((ROOT / "registry/server.json").read_text())
    assert manifest["version"] == "1.0.2"
    assert manifest["name"] == "io.github.Irishman-Management-LLC/hunterkiller"
    assert manifest["remotes"] == [
        {"type": "streamable-http", "url": "https://hunterkiller.io/mcp"}]
    assert "packages" not in manifest

def test_cursor_plugin_uses_unauthenticated_health_door():
    config = json.loads((ROOT / "mcp.json").read_text())
    assert config["mcpServers"]["hunterkiller"] == {
        "type": "streamable-http", "url": "https://hunterkiller.io/mcp"}
