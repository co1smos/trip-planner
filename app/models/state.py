from typing import Any, Dict

from pydantic import BaseModel

class AgentState(BaseModel):
    run_id: str
    trace_id: str
    request: dict[str, Any]
    category: str | None = None
    plan_steps: list[dict[str, Any]]
    observations: list[dict[str, Any]]
    result: dict[str, Any] | None
    last_node: str | None
    errors: list[dict[str, Any]]

def summarize_state(state: AgentState) -> dict[str, Any]:
    summary = {
        "run_id": state.run_id,
        "last_node": state.last_node,
        "plan_steps_count": len(state.plan_steps),
        "observations_count": len(state.observations),
    }
    return summary

