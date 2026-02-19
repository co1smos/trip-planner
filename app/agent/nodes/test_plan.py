import pytest

from app.models.state import AgentState
from app.agent.nodes.plan import plan_node


@pytest.mark.asyncio
async def test_plan_node_sets_plan_steps():
    s = AgentState(
        run_id="rid",
        trace_id="tid",
        request={"query": "go", "constraints": None},
        category="city",
        plan_steps=[],
        observations=[],
        result=None,
        last_node=None,
        errors=[],
    )
    out = await plan_node(s)
    assert isinstance(out.plan_steps, list)
    assert len(out.plan_steps) > 0
    assert out.last_node is not None
