# app/agent/nodes/test_execute_m2.py
import pytest

import app.agent.nodes.execute as exec_mod
from app.models.tools import ToolResult, ToolError
from pydantic import BaseModel


def _build_state_with_plan_steps(steps):
    from app.models.state import AgentState  # local import
    fields = getattr(AgentState, "model_fields", {}) or {}
    data = {}

    if "run_id" in fields:
        data["run_id"] = "rid"
    if "trace_id" in fields:
        data["trace_id"] = "t1"
    if "request" in fields:
        data["request"] = {"query": "x", "constraints": None}
    if "plan_steps" in fields:
        data["plan_steps"] = steps
    if "observations" in fields:
        data["observations"] = []
    if "errors" in fields:
        data["errors"] = []
    if "last_node" in fields:
        data["last_node"] = None
    if "result" in fields:
        data["result"] = None

    return AgentState.model_construct(**data)


class _FakeRegistry:
    def __init__(self, results):
        self._results = list(results)
        self.calls = []

    async def call(self, tool_name, args, *, timeout_s=None):  # noqa: ANN001
        self.calls.append((tool_name, args))
        return self._results.pop(0)


@pytest.mark.anyio
async def test_execute_records_tool_error_and_continues(monkeypatch):
    """
    If one tool returns ok=False, execute should still:
    - record the observation
    - continue to next step (if your policy is continue)
    """
    class _Out(BaseModel):
            tool: str
            value: int 
    good = ToolResult(ok=True, data=_Out(tool="x", value=1), error=None, meta=None)
    bad = ToolResult(ok=False, data=None, error=ToolError(type="TOOL_EXCEPTION", message="boom", retryable=False, details=None), meta=None)

    reg = _FakeRegistry([bad, good])

    # Patch build_registry() or get_registry() used by execute_node
    if hasattr(exec_mod, "build_registry"):
        monkeypatch.setattr(exec_mod, "build_registry", lambda: reg)
    elif hasattr(exec_mod, "get_registry"):
        monkeypatch.setattr(exec_mod, "get_registry", lambda: reg)
    else:
        # last resort: execute_node may import registry module-level
        import app.tools.registry as reg_mod
        monkeypatch.setattr(reg_mod, "build_registry", lambda: reg)

    steps = [
        {"tool": "search_places", "args": {"destination": "Tokyo", "limit": 3}},
        {"tool": "estimate_budget", "args": {"days": 3}},
    ]
    state = _build_state_with_plan_steps(steps)

    out = await exec_mod.execute_node(state)

    assert len(out.observations) == 2
    assert out.observations[0]["tool"] == "search_places"
    assert out.observations[0]["result"]["ok"] is False
    assert out.observations[1]["tool"] == "estimate_budget"
    assert out.observations[1]["result"]["ok"] is True
    assert len(reg.calls) == 2