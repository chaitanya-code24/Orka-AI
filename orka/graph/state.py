from typing import TypedDict


class AgentState(TypedDict):
    input: str
    steps: list[str]
    current_step: str
    tool_result: str
    final_output: str
    status: str
