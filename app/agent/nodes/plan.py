from app.models.state import AgentState, summarize_state
from app.llm.client import get_llm_client
from app.llm.schemas import ParsedConstraints
from app.trace.tracer import span_start, span_end, span_error

NODE_ID = "plan"

async def plan_node(state: AgentState) -> AgentState:
    #TODO: add real plan logic later (plan with LLM)
    span_start(state.trace_id, NODE_ID, summarize_state(state))
    try:
        llm_client = get_llm_client()
        constraints = await llm_client.parse_constraints(query=state.request["query"], constraints_hint=state.request["constraints"])
        constraints = ParsedConstraints.model_validate(constraints).model_dump()  # validate final merged constraints against schema
    except Exception as e:
        span_error(state.trace_id, NODE_ID, {"error": str(e)})
        state.errors.append({"node": NODE_ID, "error": str(e)})
        constraints = state.request.get("constraints", {})

    plan_steps = [
        {
            "tool": "search_places",
            "args": {"query": state.request["query"]},
        },
    ]

    estimate_budget_args = {}
    if 'days' in constraints and constraints["days"] is not None:
        estimate_budget_args["days"] = constraints["days"]
    if 'budget' in constraints and constraints["budget"] is not None and constraints["budget"].get("currency", None) is not None:
        estimate_budget_args["currency"] = constraints["budget"]["currency"]
    if estimate_budget_args != {}:
        plan_steps.append({
            "tool": "estimate_budget",
            "args": estimate_budget_args,
        })
    
    weather_hint_args = {}
    if 'destination' in constraints and constraints["destination"] is not None:
        weather_hint_args["destination"] = constraints["destination"]
    if weather_hint_args != {}:
        plan_steps.append({
            "tool": "weather_hint",
            "args": weather_hint_args,
        })

    state.plan_steps = plan_steps
    state.last_node = NODE_ID
    span_end(state.trace_id, NODE_ID, summarize_state(state))
    return state