from app.models.state import AgentState, summarize_state
from app.trace.tracer import span_start, span_end

NODE_ID = "classify"

async def classify_node(state: AgentState) -> AgentState:
    #TODO: add real classification logic here
    span_start(state.trace_id, NODE_ID, summarize_state(state))
    category = "relax"
    state.category = category
    state.last_node = NODE_ID
    span_end(state.trace_id, NODE_ID, summarize_state(state))
    return state
