"""Real framework constructors with fixture HTTP only. No model or service calls."""
import io
import json

import hunterkiller_langchain as hk
from hunterkiller_langchain import create_levels_tool as langchain_tool
from hunterkiller_crewai import create_levels_tool as crewai_tool
from hunterkiller_composio import create_levels_tool as composio_tool

DATA = {"ok": True, "tier": "delayed", "delay_sec": 7200, "age_sec": 7300, "walls": [], "truth": {"unmeasured": True}}


def test_frameworks_call_the_same_transport_and_preserve_truth(monkeypatch):
    seen = []
    def read(request, timeout):
        seen.append(request)
        return io.BytesIO(json.dumps(DATA).encode())
    monkeypatch.setattr(hk.urllib.request, "urlopen", read)
    lc = langchain_tool()
    assert lc.invoke({"symbol": "BTCUSDT"}) == DATA
    assert set(lc.args) == {"symbol"}
    crew = crewai_tool()
    assert json.loads(crew.run(symbol="BTCUSDT")) == DATA
    assert set(crew.args_schema.model_fields) == {"symbol"}
    assert len(seen) == 2
    assert all(r.get_header("Authorization") is None for r in seen)


def test_composio_registers_a_real_standalone_tool_without_network():
    from composio import Composio
    client = Composio(api_key="fixture-not-a-real-key")
    definition = composio_tool(client)
    assert definition is not None
