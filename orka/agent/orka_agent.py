from pathlib import Path

from dotenv import load_dotenv

import orka.tools  # noqa: F401
from orka.config.loader import load_config
from orka.core.exceptions import GraphExecutionError, ValidationError
from orka.core.results import AgentRunResult, StepResult
from orka.core.run_store import BaseRunStore, SQLiteRunStore
from orka.core.storage import get_default_storage
from orka.graph.builder import build_graph
from orka.graph.state import AgentState
from orka.tools import get_tool_definition


class OrkaAgent:
    """Public entry point for running Orka LangGraph workflows."""

    def __init__(self, config_path: str, run_store: BaseRunStore | None = None):
        self.config_path = Path(config_path)
        load_dotenv(self.config_path.parent / ".env")

        self.config = load_config(str(self.config_path))
        storage_path = str(self.config_path.parent / self.config.storage_path)
        self.storage = get_default_storage(storage_path)
        self.run_store = run_store or SQLiteRunStore(self.storage)
        self._initialize_tools()
        self.graph = build_graph()

    def _initialize_tools(self) -> None:
        for tool_name in self.config.tools:
            get_tool_definition(tool_name)

    def run(self, query: str) -> dict[str, object]:
        """Run the configured LangGraph workflow for a user query."""
        if not isinstance(query, str) or not query.strip():
            raise ValidationError("Query must be a non-empty string")

        result = AgentRunResult(
            success=False,
            status="started",
            output=None,
            steps=[],
            errors=[],
            message="Run started.",
        )

        initial_state: AgentState = {
            "run_id": result.run_id,
            "input": query.strip(),
            "available_tools": self.config.tools,
            "retry_count": 0,
            "max_retries": 1,
            "context": {},
            "steps": [],
            "current_step": "",
            "tool_result": None,
            "completed_steps": [],
            "final_output": None,
            "errors": [],
            "status": "idle",
        }

        try:
            final_state = self.graph.invoke(initial_state)
        except Exception as exc:
            result.status = "failed"
            result.errors.append(str(exc))
            result.message = "Graph execution failed."
            self.run_store.save_run(result.run_id, result.to_dict())
            raise GraphExecutionError(str(exc)) from exc

        completed_steps = [StepResult(**step) for step in final_state["completed_steps"]]
        result.success = final_state["status"] == "end" and not final_state["errors"] and bool(completed_steps)
        result.status = "completed" if result.success else final_state["status"]
        result.output = final_state["final_output"] or final_state["tool_result"]
        result.errors = final_state["errors"]
        result.steps = completed_steps
        if result.success:
            result.message = "Request completed successfully."
        elif final_state["status"] == "end" and not completed_steps:
            result.message = "No configured workflow steps matched the request."
        else:
            result.message = "Request completed with issues."
        self.run_store.save_run(result.run_id, result.to_dict())
        return result.to_dict()

    def get_run(self, run_id: str) -> dict[str, object] | None:
        return self.run_store.get_run(run_id)

    def list_runs(self) -> list[dict[str, object]]:
        return self.run_store.list_runs()
