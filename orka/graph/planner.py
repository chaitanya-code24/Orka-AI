import json
import re
from dataclasses import dataclass, field
from typing import Any, Protocol

from orka.tools import get_tool_definition


@dataclass
class Plan:
    steps: list[str] = field(default_factory=list)
    context: dict[str, Any] = field(default_factory=dict)


class Planner(Protocol):
    def plan(self, query: str, available_tools: list[str]) -> Plan:
        """Return ordered tool steps and shared execution context for a query."""


class RuleBasedPlanner:
    """Deterministic planner used as the offline fallback."""

    def plan(self, query: str, available_tools: list[str]) -> Plan:
        available = set(available_tools)
        planned_steps: list[str] = []

        lowered_query = query.lower()
        if "customer" in lowered_query and "create_customer_tool" in available:
            planned_steps.append("create_customer_tool")
        if "email" in lowered_query and "send_email_tool" in available:
            planned_steps.append("send_email_tool")

        return Plan(steps=planned_steps, context=extract_context(query))


class LLMPlanner:
    """Planner that asks a chat model for structured tool steps."""

    def __init__(self, llm: Any, fallback: Planner | None = None):
        self.llm = llm
        self.fallback = fallback or RuleBasedPlanner()

    def plan(self, query: str, available_tools: list[str]) -> Plan:
        prompt = self._build_prompt(query, available_tools)

        try:
            response = self.llm.invoke(prompt)
            content = getattr(response, "content", response)
            plan = self._parse_plan(str(content), available_tools)
        except Exception:
            return self.fallback.plan(query, available_tools)

        if not plan.steps:
            return self.fallback.plan(query, available_tools)
        return plan

    def _build_prompt(self, query: str, available_tools: list[str]) -> str:
        tool_summaries = []
        for tool_name in available_tools:
            definition = get_tool_definition(tool_name)
            tool_summaries.append(
                {
                    "name": definition.name,
                    "description": definition.description,
                    "parameters": definition.parameters,
                }
            )

        return (
            "You are Orka's planner. Convert the user request into an ordered JSON plan.\n"
            "Return only JSON with this shape:\n"
            '{"steps": ["tool_name"], "context": {"key": "value"}}\n'
            "Only use tool names from the available tools. Include context values needed by the tools.\n\n"
            f"Available tools: {json.dumps(tool_summaries)}\n"
            f"User request: {query}"
        )

    def _parse_plan(self, content: str, available_tools: list[str]) -> Plan:
        raw = _extract_json_object(content)
        payload = json.loads(raw)

        steps = payload.get("steps", [])
        context = payload.get("context", {})
        if not isinstance(steps, list) or not isinstance(context, dict):
            return Plan()

        allowed = set(available_tools)
        valid_steps = [step for step in steps if isinstance(step, str) and step in allowed]
        return Plan(steps=valid_steps, context=context)


def extract_context(query: str) -> dict[str, Any]:
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


def _extract_json_object(content: str) -> str:
    stripped = content.strip()
    if stripped.startswith("```"):
        stripped = re.sub(r"^```(?:json)?\s*", "", stripped, flags=re.IGNORECASE)
        stripped = re.sub(r"\s*```$", "", stripped)

    match = re.search(r"\{.*\}", stripped, re.DOTALL)
    if not match:
        raise ValueError("Planner response did not contain a JSON object")
    return match.group(0)


def _clean_capture(value: str) -> str:
    return value.strip().rstrip(".,")


def _looks_like_missing_name(value: str) -> bool:
    lowered = value.lower()
    return lowered.startswith(("and ", "to ", "message ")) or lowered in {"and", "to", "message"} or "send email" in lowered
