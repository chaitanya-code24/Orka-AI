import re
from typing import Any

from orka.core.exceptions import ToolExecutionError
from orka.core.results import StepResult
from orka.graph.state import AgentState
from orka.tools import invoke_tool


def planner_node(state: AgentState) -> AgentState:
    query = state["input"]
    available_tools = set(state["available_tools"])
    planned_steps: list[str] = []

    lowered_query = query.lower()
    if "customer" in lowered_query and "create_customer_tool" in available_tools:
        planned_steps.append("create_customer_tool")
    if "email" in lowered_query and "send_email_tool" in available_tools:
        planned_steps.append("send_email_tool")

    if not planned_steps:
        return {
            **state,
            "steps": [],
            "current_step": "",
            "tool_result": None,
            "final_output": {"message": "No matching tools were planned for the request."},
            "status": "end",
        }

    context = _extract_context(query)
    remaining_steps = planned_steps[1:]
    return {
        **state,
        "context": context,
        "steps": remaining_steps,
        "current_step": planned_steps[0],
        "tool_result": None,
        "final_output": None,
        "status": "planned",
    }


def tool_node(state: AgentState) -> AgentState:
    if state["status"] == "end":
        return state

    current_step = state["current_step"]
    if not current_step:
        return {
            **state,
            "tool_result": None,
            "status": "end",
            "final_output": state["final_output"] or {"message": "No tool was selected for execution."},
        }

    try:
        tool_result = _execute_tool(current_step, state["context"])
    except Exception as exc:
        step_result = StepResult(tool_name=current_step, success=False, error=str(exc))
        return {
            **state,
            "tool_result": None,
            "completed_steps": [*state["completed_steps"], step_result.to_dict()],
            "errors": [*state["errors"], str(exc)],
            "retry_count": state["retry_count"] + 1,
            "status": "retry",
        }

    step_result = StepResult(tool_name=current_step, success=True, output=tool_result)
    return {
        **state,
        "tool_result": tool_result,
        "completed_steps": [*state["completed_steps"], step_result.to_dict()],
        "status": "tool_executed",
    }


def validator_node(state: AgentState) -> AgentState:
    if state["status"] == "end":
        return state

    if state["tool_result"] is None:
        if state["retry_count"] >= state["max_retries"]:
            return {
                **state,
                "status": "end",
                "final_output": {
                    "steps": state["completed_steps"],
                    "message": "Tool execution failed after reaching the retry limit.",
                },
            }
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
        "final_output": {
            "steps": state["completed_steps"],
            "last_result": state["tool_result"],
        },
        "status": "end",
    }


def decision_node(state: AgentState) -> str:
    status = state["status"]
    if status == "retry":
        return "retry"
    if status == "continue":
        return "continue"
    return "end"


def _execute_tool(tool_name: str, context: dict[str, Any]) -> dict[str, Any]:
    try:
        if tool_name == "create_customer_tool":
            return invoke_tool(
                tool_name,
                name=context["customer_name"],
                city=context["customer_city"],
            )
        if tool_name == "send_email_tool":
            return invoke_tool(
                tool_name,
                to=context["email_to"],
                message=context["email_message"],
            )
        return invoke_tool(tool_name)
    except Exception as exc:
        raise ToolExecutionError(f"Tool '{tool_name}' failed: {exc}") from exc


def _extract_context(query: str) -> dict[str, Any]:
    email_match = re.search(r"[\w.+-]+@[\w.-]+\.\w+", query)
    city_match = re.search(r"\b(?:in|from)\s+([A-Za-z][A-Za-z\s-]{1,40}?)(?=\s+(?:and|message|to)\b|[.,]|$)", query, re.IGNORECASE)
    name_match = re.search(r"\bcustomer(?:\s+named)?\s+([A-Za-z][A-Za-z\s'-]{1,40}?)(?=\s+(?:in|from|and|to|message)\b|[.,]|$)", query, re.IGNORECASE)
    message_match = re.search(r"\bmessage\s+(.+)$", query, re.IGNORECASE)

    customer_name = _clean_capture(name_match.group(1)) if name_match else "Demo Customer"
    customer_city = _clean_capture(city_match.group(1)) if city_match else "Pune"
    email_to = email_match.group(0) if email_match else "customer@example.com"
    email_message = _clean_capture(message_match.group(1)) if message_match else "Welcome from Orka."

    if _looks_like_missing_name(customer_name):
        customer_name = "Demo Customer"

    return {
        "customer_name": customer_name,
        "customer_city": customer_city,
        "email_to": email_to,
        "email_message": email_message,
    }


def _clean_capture(value: str) -> str:
    return value.strip().rstrip(".,")


def _looks_like_missing_name(value: str) -> bool:
    lowered = value.lower()
    return lowered.startswith(("and ", "to ", "message ")) or lowered in {"and", "to", "message"} or "send email" in lowered
