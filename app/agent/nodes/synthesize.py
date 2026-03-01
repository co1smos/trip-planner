from app.models.state import AgentState, summarize_state
from app.trace.tracer import span_start, span_end

NODE_ID = "synthesize"

# Post Processing Layer
async def synthesize_node(state: AgentState) -> AgentState:
    #TODO: add real execution logic later
    span_start(state.trace_id, NODE_ID, summarize_state(state))
    tools_used = [obs.get("tool") for obs in state.observations if "tool" in obs]
    tools_error = [obs.get("tool") for obs in state.observations if obs.get("result", {}).get("ok") is False]
    state.result = {"result": "finished", "tools_used": tools_used, "tools_error": tools_error}
    state.last_node = NODE_ID
    span_end(state.trace_id, NODE_ID, summarize_state(state))
    return state