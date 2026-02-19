import pytest

from app.models.state import AgentState
from app.agent.nodes.synthesize import synthesize_node


@pytest.mark.asyncio
async def test_synthesize_node_sets_result():
    s = AgentState(
        run_id="rid",
        trace_id="tid",
        request={"query": "go", "constraints": None},
        category="city",
        plan_steps=[{"tool": "dummy", "args": {}}],
        observations=[{"tool": "dummy", "ok": True}],
        result=None,
        last_node=None,
        errors=[],
    )
    out = await synthesize_node(s)
    assert out.result is not None
    assert out.last_node is not None
