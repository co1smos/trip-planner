import pytest
from app.models.state import AgentState


@pytest.mark.anyio
async def test_plan_node_emits_executable_plan_steps():
    from app.agent.nodes.plan import plan_node

    state = AgentState(
        run_id="rid",
        trace_id="tid",
        request={"query": "tokyo", "constraints": {"days": 3}},
        category="city",
        plan_steps=[],
        observations=[],
        result=None,
        last_node=None,
        errors=[],
    )

    out = await plan_node(state)

    assert out.last_node is not None
    assert isinstance(out.plan_steps, list)
    assert len(out.plan_steps) >= 1

    step0 = out.plan_steps[0]
    assert isinstance(step0, dict)
    # M2 plan_steps contract
    assert "tool" in step0
    assert "args" in step0
    assert isinstance(step0["tool"], str)
    assert isinstance(step0["args"], dict)