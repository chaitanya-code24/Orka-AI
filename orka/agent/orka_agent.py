from pathlib import Path

from dotenv import load_dotenv

import orka.tools  # noqa: F401
from orka.config.loader import load_config
from orka.graph.builder import build_graph
from orka.graph.state import AgentState
from orka.tools import get_tool


class OrkaAgent:
    """Public entry point for running Orka LangGraph workflows."""

    def __init__(self, config_path: str):
        self.config_path = Path(config_path)
        load_dotenv(self.config_path.parent / ".env")

        self.config = load_config(str(self.config_path))
        self._initialize_tools()
        self.graph = build_graph()

    def _initialize_tools(self) -> None:
        for tool_name in self.config.tools:
            get_tool(tool_name)

    def run(self, query: str):
        """Run the configured LangGraph workflow for a user query."""
        initial_state: AgentState = {
            "input": query,
            "steps": [],
            "current_step": "",
            "tool_result": "",
            "final_output": "",
            "status": "idle",
        }

        final_state = self.graph.invoke(initial_state)
        return final_state["final_output"] or final_state["tool_result"]
