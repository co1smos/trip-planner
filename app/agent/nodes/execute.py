from app.tools.registry import build_registry, ToolRegistry
from app.models.state import AgentState, summarize_state
from app.models.tools import ToolResult, ToolError
from app.trace.tracer import span_start, span_end

NODE_ID = "execute" 

async def execute_node(state: AgentState) -> AgentState:
    #TODO: add real execution logic later
    span_start(state.trace_id, NODE_ID, summarize_state(state))
    registry = build_registry()
    for step in state.plan_steps:
        tool_name = step.get("tool")
        args = step.get("args")
        if tool_name and args:
            result = await registry.call(tool_name, args)
            state.observations.append({
                "tool": tool_name,
                "args": args,
                "result": result.model_dump() if result else None,
            })

    state.last_node = NODE_ID
    span_end(state.trace_id, NODE_ID, summarize_state(state))
    return state