from app.models.state import AgentState, summarize_state
from app.trace.tracer import span_start, span_end

NODE_ID = "synthesize"

async def synthesize_node(state: AgentState) -> AgentState:
    #TODO: add real execution logic later
    span_start(state.trace_id, NODE_ID, summarize_state(state))
    result = {"result":"finshed"}
    state.result = result
    state.last_node = "synthesize"
    span_end(state.trace_id, NODE_ID, summarize_state(state))
    return state