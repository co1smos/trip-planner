import pytest

from app.agent.graph import build_graph
from app.models.state import AgentState


async def _run_graph(graph, state_dict):
    if hasattr(graph, "ainvoke"):
        return await graph.ainvoke(state_dict)
    return graph.invoke(state_dict)


@pytest.mark.asyncio
async def test_build_graph_smoke():
    g = build_graph()
    assert g is not None

    init = AgentState(
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
    out = await _run_graph(g, init.model_dump())
    final = AgentState.model_validate(out)
    assert final.result is not None
    assert final.last_node is not None
