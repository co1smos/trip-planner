# app/agent/nodes/test_plan_node_m35.py
import pytest

import app.agent.nodes.plan as plan_mod
from app.llm.schemas import ParsedConstraints


def _build_state(run_id: str = "rid", query: str = "go tokyo", api_constraints=None):
    """
    Build a minimal AgentState without knowing your exact field set.
    We use Pydantic's model_construct to avoid brittle required-field coupling.
    """
    from app.models.state import AgentState  # local import to avoid import-time side effects

    fields = getattr(AgentState, "model_fields", {}) or {}
    data = {}

    # Common fields used in your milestones
    if "run_id" in fields:
        data["run_id"] = run_id
    if "trace_id" in fields:
        data["trace_id"] = "t1"
    if "request" in fields:
        # request should include query + constraints
        data["request"] = {"query": query, "constraints": api_constraints}
    if "category" in fields:
        data["category"] = None
    if "plan_steps" in fields:
        data["plan_steps"] = []
    if "observations" in fields:
        data["observations"] = []
    if "result" in fields:
        data["result"] = None
    if "last_node" in fields:
        data["last_node"] = None
    if "errors" in fields:
        data["errors"] = []

    # Construct without validation to be robust across your internal changes
    return AgentState.model_construct(**data)


class _FakeLLM:
    def __init__(self, out=None, exc=None):
        self._out = out
        self._exc = exc

    async def parse_constraints(self, *, query: str, constraints_hint):  # noqa: ANN001
        if self._exc is not None:
            raise self._exc
        return self._out


@pytest.mark.anyio
async def test_plan_node_uses_llm_and_emits_executable_steps(monkeypatch):
    """
    Success path:
    - LLM returns parsed constraints
    - plan_node produces executable plan_steps (tool + args)
    - must include estimate_budget at minimum
    """
    fake = _FakeLLM(out=ParsedConstraints(destination="Tokyo", days=5, interests=["food"]).model_dump())
    monkeypatch.setattr(plan_mod, "get_llm_client", lambda: fake)

    state = _build_state(api_constraints={"budget": {"currency": "USD", "total": 2000}})
    out = await plan_mod.plan_node(state)

    assert getattr(out, "plan_steps", None) is not None
    steps = out.plan_steps
    assert isinstance(steps, list)
    assert len(steps) >= 1
    assert any(s.get("tool") == "estimate_budget" for s in steps)

    # ensure args are present and dict
    for s in steps:
        assert "tool" in s
        assert "args" in s
        assert isinstance(s["args"], dict)


@pytest.mark.anyio
async def test_plan_node_llm_timeout_degrades_to_api_constraints(monkeypatch):
    """
    Failure path: LLM timeout/error must not crash.
    Plan must still be executable (at least estimate_budget), using API constraints or defaults.
    Also should record an error in state.errors (or a stable marker).
    """
    class _Timeout(Exception):
        pass

    fake = _FakeLLM(exc=_Timeout("timeout"))
    monkeypatch.setattr(plan_mod, "get_llm_client", lambda: fake)

    state = _build_state(api_constraints={"destination": "Tokyo", "days": 3})
    out = await plan_mod.plan_node(state)

    steps = out.plan_steps
    assert any(s.get("tool") == "estimate_budget" for s in steps)

    # error marker (prefer state.errors)
    if hasattr(out, "errors"):
        assert isinstance(out.errors, list)
        assert len(out.errors) >= 1


@pytest.mark.anyio
async def test_plan_node_llm_invalid_schema_degrades(monkeypatch):
    """
    Failure path: LLM returns invalid schema (e.g., days is string).
    plan_node must degrade (no crash) and still output executable steps.
    """
    fake = _FakeLLM(out={"destination": "Tokyo", "days": "five"})
    monkeypatch.setattr(plan_mod, "get_llm_client", lambda: fake)

    state = _build_state(api_constraints={"days": 4})
    out = await plan_mod.plan_node(state)

    steps = out.plan_steps
    assert any(s.get("tool") == "estimate_budget" for s in steps)

    if hasattr(out, "errors"):
        assert len(out.errors) >= 1