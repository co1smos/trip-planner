from app.models.state import AgentState, summarize_state
from app.trace.tracer import span_start, span_end

NODE_ID = "plan"

async def plan_node(state: AgentState) -> AgentState:
    #TODO: add real plan logic later
    span_start(state.trace_id, NODE_ID, summarize_state(state))
    plan_steps = [
        {"step1": "unknown"},
        {"step2": "unknown"},
    ]
    state.plan_steps = plan_steps
    state.last_node = "plan"
    span_end(state.trace_id, NODE_ID, summarize_state(state))
    return state