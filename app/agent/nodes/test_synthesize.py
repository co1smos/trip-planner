# app/agent/nodes/test_synthesize_m35.py
import pytest

import app.agent.nodes.synthesize as syn_mod


def _build_state_with_observations(observations, errors=None):
    from app.models.state import AgentState
    fields = getattr(AgentState, "model_fields", {}) or {}
    data = {}

    if "run_id" in fields:
        data["run_id"] = "rid"
    if "trace_id" in fields:
        data["trace_id"] = "t1"
    if "request" in fields:
        data["request"] = {"query": "x", "constraints": None}
    if "plan_steps" in fields:
        data["plan_steps"] = []
    if "observations" in fields:
        data["observations"] = observations
    if "errors" in fields:
        data["errors"] = errors or []
    if "result" in fields:
        data["result"] = None
    if "last_node" in fields:
        data["last_node"] = None

    return AgentState.model_construct(**data)


@pytest.mark.anyio
async def test_synthesize_includes_tools_used_and_budget_when_available():
    obs = [
        {
            "tool": "estimate_budget",
            "args": {"days": 5},
            "result": {"ok": True, "data": {"breakdown": {"food": 100}}, "error": None},
        },
        {
            "tool": "search_places",
            "args": {"destination": "Tokyo", "limit": 2},
            "result": {"ok": True, "data": {"places": [{"name": "A"}, {"name": "B"}]}, "error": None},
        },
    ]
    state = _build_state_with_observations(obs)

    out = await syn_mod.synthesize_node(state)

    assert out.result is not None
    assert isinstance(out.result, dict)

    # These keys are the "M3.5 stable result" expectation
    # If your synthesize uses different names, adjust here.
    tools_used = out.result.get("tools_used") or out.result.get("meta", {}).get("tools_used")
    assert tools_used is not None
    assert "estimate_budget" in tools_used

    budget = out.result.get("budget")
    assert budget is not None


@pytest.mark.anyio
async def test_synthesize_handles_tool_error_gracefully_and_adds_note():
    obs = [
        {
            "tool": "search_places",
            "args": {"destination": "Mars", "limit": 2},
            "result": {"ok": False, "data": None, "error": {"type": "NOT_FOUND", "message": "no data", "retryable": False}},
        }
    ]
    state = _build_state_with_observations(obs, errors=[{"type": "llm_timeout", "message": "timeout"}])

    out = await syn_mod.synthesize_node(state)

    assert out.result is not None
    notes = out.result.get("notes") or out.result.get("assumptions") or []
    assert isinstance(notes, list)
    # should mention either tool failure or llm degradation
    joined = " ".join(str(x).lower() for x in notes)
    assert ("timeout" in joined) or ("not_found" in joined) or ("no data" in joined)