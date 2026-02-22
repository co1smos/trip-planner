from app.models.state import AgentState
from app.agent.nodes.classify import classify_node
from app.agent.nodes.plan import plan_node
from app.agent.nodes.execute import execute_node
from app.agent.nodes.synthesize import synthesize_node
from langgraph.graph.state import CompiledStateGraph, StateGraph, START, END

def build_graph() -> CompiledStateGraph:
    agent_builder = StateGraph(AgentState)

    agent_builder.add_node("classify", classify_node)
    agent_builder.add_node("plan", plan_node)
    agent_builder.add_node("execute", execute_node)
    agent_builder.add_node("synthesize", synthesize_node)

    agent_builder.add_edge(START, "classify")
    agent_builder.add_edge("classify", "plan")
    agent_builder.add_edge("plan", "execute")
    agent_builder.add_edge("execute", "synthesize")
    agent_builder.add_edge("synthesize", END)

    graph = agent_builder.compile()
    return graph
    