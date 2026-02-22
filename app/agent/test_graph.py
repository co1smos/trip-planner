import pytest

from app.agent.graph import build_graph
from app.models.state import AgentState


async def _run_graph(graph, state_dict):
    # LangGraph compiled graphs commonly expose ainvoke; some expose invoke
    if hasattr(graph, "ainvoke"):
        return await graph.ainvoke(state_dict)
    if hasattr(graph, "invoke"):
        return graph.invoke(state_dict)
    raise AssertionError("Graph is not executable: missing ainvoke/invoke")


@pytest.mark.anyio
async def test_build_graph_returns_executable():
    g = build_graph()
    assert g is not None
    assert hasattr(g, "ainvoke") or hasattr(g, "invoke")


@pytest.mark.anyio
async def test_graph_runs_end_to_end_and_produces_result():
    g = build_graph()

    init = AgentState(
        run_id="rid",
        trace_id="tid",
        request={"query": "go tokyo", "constraints": {"days": 5}},
        category=None,
        plan_steps=[],
        observations=[],
        result=None,
        last_node=None,
        errors={},
    )

    out = await _run_graph(g, init.model_dump())
    assert isinstance(out, dict)

    final = AgentState.model_validate(out)
    assert final.result is not None
    assert final.last_node is not None

    # Strong expectation: last node should be synthesize-ish.
    # If you name it differently, change this assert to match your node name.
    assert "synth" in final.last_node.lower()
