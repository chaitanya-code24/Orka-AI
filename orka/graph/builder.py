from langgraph.graph import END, START, StateGraph

from orka.graph.planner import Planner
from orka.graph.nodes import decision_node, planner_node, tool_node, validator_node
from orka.graph.state import AgentState


def build_graph(planner: Planner | None = None):
    workflow = StateGraph(AgentState)

    workflow.add_node("planner", lambda state: planner_node(state, planner=planner))
    workflow.add_node("tool", tool_node)
    workflow.add_node("validator", validator_node)

    workflow.add_edge(START, "planner")
    workflow.add_edge("planner", "tool")
    workflow.add_edge("tool", "validator")
    workflow.add_conditional_edges(
        "validator",
        decision_node,
        {
            "continue": "tool",
            "retry": "tool",
            "end": END,
        },
    )

    return workflow.compile()
