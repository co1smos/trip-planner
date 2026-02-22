from app.models.state import AgentState, summarize_state
from app.trace.tracer import span_start, span_end

NODE_ID = "execute"

async def execute_node(state: AgentState) -> AgentState:
    #TODO: add real execution logic later
    span_start(state.trace_id, NODE_ID, summarize_state(state))
    observations = [
        {"observation1": "unknown"},
        {"observation2": "unknown"},
    ]
    state.observations = observations
    state.last_node = "execute"
    span_end(state.trace_id, NODE_ID, summarize_state(state))
    return state