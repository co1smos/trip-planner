import pytest

from app.models.state import AgentState
from app.agent.nodes.classify import classify_node


@pytest.mark.asyncio
async def test_classify_node_sets_category_and_last_node():
    s = AgentState(
        run_id="rid",
        trace_id="tid",
        request={"query": "go", "constraints": None},
        category=None,
        plan_steps=[],
        observations=[],
        result=None,
        last_node=None,
        errors=[],
    )
    out = await classify_node(s)
    assert out.category is not None
    assert out.last_node is not None
