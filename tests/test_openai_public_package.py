"""A distinct public app may differ from the retained package only in its name."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1] / "agent-integrations"
BASELINE_SHA = "3a16ee8ec1d4b3517c02b439ef9cb5982e2f4517abfe6759541010ee049991c8"


def test_distinct_public_identity_preserves_existing_package():
    source = ROOT / "openai/hunterkiller-openai-app.zip"
    assert hashlib.sha256(source.read_bytes()).hexdigest() == BASELINE_SHA
    public = ROOT / "openai-public"
    subprocess.run([sys.executable, str(public / "build_package.py"), "--check"], check=True)
    with zipfile.ZipFile(source) as old, zipfile.ZipFile(public / "hunterkiller-public.zip") as new:
        assert new.namelist() == old.namelist()
        for name in new.namelist():
            assert new.read(name) == (public / "package" / name).read_bytes()
            if name != "plugin.json":
                assert new.read(name) == old.read(name)
        before = json.loads(old.read("plugin.json"))
        after = json.loads(new.read("plugin.json"))
        assert after["name"] == "hunterkiller-public"
        assert after["version"] == "0.1.1"
        assert after["extensions"]["com.openai"]["interface"]["displayName"] == "Hunter Killer"
        after["name"] = before["name"]
        assert after == before
        assert not any("apps/" in name or name.endswith(".app.json") for name in new.namelist())
        manifest = new.read("plugin.json").decode().lower()
        assert not any(binding in manifest for binding in ('"app_id"', '"appid"', '"update_url"', '"updateurl"'))
