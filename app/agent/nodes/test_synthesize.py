import pytest
from app.models.state import AgentState
from app.agent.nodes.synthesize import synthesize_node


@pytest.mark.anyio
async def test_synthesize_node_sets_result_and_last_node():
    # observations can be empty or non-empty; synthesize should still produce some result dict
    state = AgentState(
        run_id="rid",
        trace_id="tid",
        request={"query": "tokyo"},
        category="city",
        plan_steps=[{"tool": "search_places", "args": {"query": "tokyo"}}],
        observations=[
            {"tool": "search_places", "args": {"query": "tokyo"}, "result": {"ok": True, "data": {"places": []}, "error": None, "meta": None}},
        ],
        result=None,
        last_node=None,
        errors=[],
    )

    out = await synthesize_node(state)

    assert out.last_node is not None
    assert out.result is not None
    assert isinstance(out.result, dict)