from typing import Any

from orka.core.exceptions import ToolExecutionError
from orka.core.results import StepResult
from orka.graph.planner import Planner, RuleBasedPlanner
from orka.graph.state import AgentState
from orka.tools import invoke_tool


def planner_node(state: AgentState, planner: Planner | None = None) -> AgentState:
    query = state["input"]
    planner = planner or RuleBasedPlanner()
    plan = planner.plan(query, state["available_tools"])
    planned_steps = plan.steps

    if not planned_steps:
        return {
            **state,
            "steps": [],
            "current_step": "",
            "tool_result": None,
            "final_output": {"message": "No matching tools were planned for the request."},
            "status": "end",
        }

    if not state.get("approved", False) and _requires_approval(planned_steps, state["approval_required_tools"]):
        return {
            **state,
            "context": plan.context,
            "steps": planned_steps[1:],
            "current_step": planned_steps[0],
            "tool_result": None,
            "final_output": {
                "approval": {
                    "required": True,
                    "planned_steps": planned_steps,
                    "context": plan.context,
                },
                "message": "Run is waiting for approval before executing tools.",
            },
            "status": "awaiting_approval",
        }

    remaining_steps = planned_steps[1:]
    return {
        **state,
        "context": plan.context,
        "steps": remaining_steps,
        "current_step": planned_steps[0],
        "tool_result": None,
        "final_output": None,
        "status": "planned",
    }


def tool_node(state: AgentState) -> AgentState:
    if state["status"] in {"end", "awaiting_approval"}:
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
    if state["status"] in {"end", "awaiting_approval"}:
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


def _requires_approval(planned_steps: list[str], approval_required_tools: list[str]) -> bool:
    if "*" in approval_required_tools:
        return True
    required = set(approval_required_tools)
    return any(step in required for step in planned_steps)


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
