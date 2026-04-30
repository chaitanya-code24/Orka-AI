from typing import Any, TypedDict


class AgentState(TypedDict):
    run_id: str
    input: str
    available_tools: list[str]
    retry_count: int
    max_retries: int
    context: dict[str, Any]
    steps: list[str]
    current_step: str
    tool_result: dict[str, Any] | None
    completed_steps: list[dict[str, Any]]
    final_output: dict[str, Any] | None
    errors: list[str]
    status: str
