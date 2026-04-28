from orka.graph.state import AgentState
from orka.tools import get_tool


def planner_node(state: AgentState) -> AgentState:
    query = state["input"].lower()
    planned_steps: list[str] = []

    if "customer" in query:
        planned_steps.append("create_customer_tool")
    if "email" in query:
        planned_steps.append("send_email_tool")

    if not planned_steps:
        return {
            **state,
            "steps": [],
            "current_step": "",
            "tool_result": "",
            "final_output": "No matching tools were planned for the request.",
            "status": "end",
        }

    remaining_steps = planned_steps[1:]
    return {
        **state,
        "steps": remaining_steps,
        "current_step": planned_steps[0],
        "tool_result": "",
        "final_output": "",
        "status": "planned",
    }


def tool_node(state: AgentState) -> AgentState:
    current_step = state["current_step"]
    if not current_step:
        return {
            **state,
            "tool_result": "",
            "status": "retry",
        }

    tool = get_tool(current_step)
    tool_result = _execute_tool(current_step, tool)
    return {
        **state,
        "tool_result": str(tool_result),
        "status": "tool_executed",
    }


def validator_node(state: AgentState) -> AgentState:
    tool_result = state["tool_result"]
    if not tool_result:
        return {
            **state,
            "status": "retry",
        }

    if state["steps"]:
        next_step = state["steps"][0]
        remaining_steps = state["steps"][1:]
        return {
            **state,
            "steps": remaining_steps,
            "current_step": next_step,
            "status": "continue",
        }

    return {
        **state,
        "final_output": tool_result,
        "status": "end",
    }


def decision_node(state: AgentState) -> str:
    status = state["status"]
    if status == "retry":
        return "retry"
    if status == "continue":
        return "continue"
    return "end"


def _execute_tool(tool_name, tool):
    if tool_name == "create_customer_tool":
        return tool(name="Demo Customer", city="Pune")
    if tool_name == "send_email_tool":
        return tool(to="customer@example.com", message="Welcome from Orka.")
    return tool()
