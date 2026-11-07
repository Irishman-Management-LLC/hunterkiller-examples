"""Manual Space callback contracts with fixture HTTP, no Gradio server or live call."""
import ast
import io
import json
import os
from pathlib import Path
import urllib.request

import pytest

EXAMPLES = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize("probe", [None, "1"])
def test_space_internal_verification_is_marked_only_when_explicit(monkeypatch, probe):
    source = ast.parse((EXAMPLES / "space/app.py").read_text())
    function = next(node for node in source.body if isinstance(node, ast.FunctionDef) and node.name == "load_levels")
    namespace = {"json": json, "os": os, "urllib": __import__("urllib"),
                 "gr": type("FixtureGradio", (), {"Error": RuntimeError})}
    exec(compile(ast.Module(body=[function], type_ignores=[]), "space_callback", "exec"), namespace)
    body = {"ok": True, "walls": [], "tier": "delayed", "delay_sec": 7200,
            "age_sec": 7312, "as_of_iso": "fixture_time"}
    seen = []
    def read(request, timeout):
        seen.append((request, timeout))
        return io.BytesIO(json.dumps(body).encode())
    monkeypatch.setattr(namespace["urllib"].request, "urlopen", read)
    if probe is None:
        monkeypatch.delenv("HK_INTERNAL_PROBE", raising=False)
    else:
        monkeypatch.setenv("HK_INTERNAL_PROBE", probe)
    rows, status, raw = namespace["load_levels"]()
    assert raw == body and rows == [] and "7312 seconds" in status
    assert len(seen) == 1 and seen[0][1] == 15
    assert seen[0][0].get_header("X-hk-probe") == probe
    assert seen[0][0].get_header("Authorization") is None
