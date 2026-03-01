import pytest

from app.models.state import AgentState


class _FakeRegistry:
    def __init__(self):
        self.calls = []

    async def call(self, tool_name, args, timeout_s=None):
        self.calls.append((tool_name, args, timeout_s))
        from pydantic import BaseModel
        from app.models.tools import ToolResult

        class _Out(BaseModel):
            tool: str

        return ToolResult(ok=True, data=_Out(tool=tool_name), error=None, meta=None)


@pytest.mark.anyio
async def test_classify_plan_execute_synthesize_nodes_contract(monkeypatch):
    from app.agent.nodes.classify import classify_node
    from app.agent.nodes.plan import plan_node
    from app.agent.nodes.execute import execute_node
    from app.agent.nodes.synthesize import synthesize_node

    import app.agent.nodes.execute as exec_mod
    fake_reg = _FakeRegistry()
    monkeypatch.setattr(exec_mod, "build_registry", lambda: fake_reg)

    state = AgentState(
        run_id="rid",
        trace_id="tid",
        request={"query": "tokyo", "constraints": {"days": 3}},
        category=None,
        plan_steps=[],
        observations=[],
        result=None,
        last_node=None,
        errors=[],
    )

    s1 = await classify_node(state)
    assert s1.last_node is not None

    s2 = await plan_node(s1)
    assert isinstance(s2.plan_steps, list)
    assert len(s2.plan_steps) >= 1
    assert "tool" in s2.plan_steps[0]
    assert "args" in s2.plan_steps[0]

    s3 = await execute_node(s2)
    assert len(fake_reg.calls) == len(s3.plan_steps)
    assert len(s3.observations) == len(s3.plan_steps)

    obs0 = s3.observations[0]
    assert {"tool", "args", "result"} <= set(obs0.keys())
    assert "ok" in obs0["result"]
    # scalable: result should be JSON-serializable dict
    assert isinstance(obs0["result"], dict)

    s4 = await synthesize_node(s3)
    assert s4.result is not None
    assert s4.last_node is not None