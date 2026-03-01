import pytest
from pydantic import BaseModel

from app.models.state import AgentState
from app.models.tools import ToolResult, ToolError
from app.agent.nodes.execute import execute_node
import app.agent.nodes.execute as exec_mod


class _FakeRegistry:
    def __init__(self):
        self.calls = []

    async def call(self, tool_name, args, timeout_s=None):
        self.calls.append((tool_name, args, timeout_s))

        class _Out(BaseModel):
            tool: str

        return ToolResult(ok=True, data=_Out(tool=tool_name), error=None, meta=None)


@pytest.mark.anyio
async def test_execute_node_calls_registry_and_writes_observations(monkeypatch):
    fake = _FakeRegistry()
    monkeypatch.setattr(exec_mod, "build_registry", lambda: fake)

    state = AgentState(
        run_id="rid",
        trace_id="tid",
        request={"query": "tokyo"},
        category="city",
        plan_steps=[
            {"tool": "search_places", "args": {"query": "tokyo"}},
            {"tool": "estimate_budget", "args": {"days": 3, "currency": "USD", "total": 1000}},
        ],
        observations=[],
        result=None,
        last_node=None,
        errors=[],
    )

    out = await execute_node(state)

    assert out.last_node is not None
    assert len(fake.calls) == 2
    assert len(out.observations) == 2

    obs0 = out.observations[0]
    assert {"tool", "args", "result"} <= set(obs0.keys())
    assert obs0["tool"] == "search_places"
    assert isinstance(obs0["args"], dict)

    # result should be JSON-serializable dict via ToolResult.model_dump()
    assert isinstance(obs0["result"], dict)
    assert "ok" in obs0["result"]
    assert obs0["result"]["ok"] is True


class _FailRegistry:
    def __init__(self, error_type: str):
        self.error_type = error_type
        self.calls = 0

    async def call(self, tool_name, args, timeout_s=None):
        self.calls += 1
        return ToolResult(
            ok=False,
            data=None,
            error=ToolError(type=self.error_type, message="x", retryable=False, details=None),
            meta=None,
        )


@pytest.mark.anyio
async def test_execute_records_tool_failures_in_observations(monkeypatch):
    from app.agent.nodes.execute import execute_node
    import app.agent.nodes.execute as exec_mod

    reg = _FailRegistry("TOOL_EXCEPTION")
    monkeypatch.setattr(exec_mod, "build_registry", lambda: reg)

    state = AgentState(
        run_id="rid",
        trace_id="tid",
        request={"query": "x"},
        category="city",
        plan_steps=[{"tool": "search_places", "args": {"query": "x"}}],
        observations=[],
        result=None,
        last_node=None,
        errors=[],
    )

    out = await execute_node(state)
    assert reg.calls == 1
    assert len(out.observations) == 1
    r = out.observations[0]["result"]
    assert r["ok"] is False
    assert r["error"]["type"] == "TOOL_EXCEPTION"