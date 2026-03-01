import pytest

from app.models.state import AgentState, summarize_state


def test_agent_state_construct_and_summarize_minimal():
    s = AgentState(
        run_id="rid",
        trace_id="tid",
        request={"query": "go tokyo", "constraints": {"days": 5}},
        category=None,
        plan_steps=[],
        observations=[],
        result=None,
        last_node=None,
        errors=[],
    )
    summary = summarize_state(s)
    assert isinstance(summary, dict)

    # must be safe summary (no big payloads)
    assert "request" not in summary
    assert "observations" not in summary
    assert "plan_steps" not in summary

    # should expose progress-ish fields
    assert summary.get("run_id") == "rid"
    assert "last_node" in summary
    assert "plan_steps_count" in summary
    assert "observations_count" in summary
