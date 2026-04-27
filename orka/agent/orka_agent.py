from pathlib import Path
from typing import Any

from dotenv import load_dotenv

from orka.config.loader import load_config


class OrkaAgent:
    """Public entry point for running Orka LangGraph workflows."""

    def __init__(self, config_path: str):
        self.config_path = Path(config_path)
        load_dotenv(self.config_path.parent / ".env")

        self.config = load_config(str(self.config_path))
        self.graph = self._initialize_graph()

    def _initialize_graph(self) -> Any:
        """Prepare the graph slot; graph construction is added in a later module."""
        return None

    def run(self, query: str):
        """Run the configured LangGraph workflow for a user query."""
        if self.graph is None:
            raise NotImplementedError("LangGraph workflow is not implemented yet.")

        initial_state = {"input": query}
        return self.graph.invoke(initial_state)
