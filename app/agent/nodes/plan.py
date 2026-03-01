from app.models.state import AgentState, summarize_state
from app.trace.tracer import span_start, span_end

NODE_ID = "plan"

async def plan_node(state: AgentState) -> AgentState:
    #TODO: add real plan logic later (plan with LLM)
    span_start(state.trace_id, NODE_ID, summarize_state(state))
    plan_steps = [
        {
            "tool": "search_places",
            "args": {"query": "plan a trip to tokyo"},
        },
        {
            "tool": "estimate_budget",
            "args": {"days": 5, "currency": "USD"},
        },
        {
            "tool": "weather_hint",
            "args": {"destination": "tokyo"},
        },
    ]
    state.plan_steps = plan_steps
    state.last_node = "plan"
    span_end(state.trace_id, NODE_ID, summarize_state(state))
    return state