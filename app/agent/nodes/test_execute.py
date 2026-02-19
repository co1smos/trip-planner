import pytest

from app.models.state import AgentState
from app.agent.nodes.execute import execute_node


@pytest.mark.asyncio
async def test_execute_node_sets_observations():
    s = AgentState(
        run_id="rid",
        trace_id="tid",
        request={"query": "go", "constraints": None},
        category="city",
        plan_steps=[{"tool": "dummy", "args": {}}],
        observations=[],
        result=None,
        last_node=None,
        errors=[],
    )
    out = await execute_node(s)
    assert isinstance(out.observations, list)
    assert len(out.observations) > 0
    assert out.last_node is not None
