from datetime import datetime
import logging
from pathlib import Path

from dotenv import load_dotenv
from langchain.agents import create_agent

from orka.config.loader import load_config
from orka.core.llm import get_llm
from orka.core.logging import log_event
from orka.core.memory import BaseMemory, get_memory
from orka.core.observability import ExecutionTrace, ToolUsageCallbackHandler
from orka.core.validation import InputValidator, SafetyValidator, ToolValidator, validation_manager
from orka.tools.registry import registry


class OrkaAgent:
    def __init__(self, config_path: str = None, memory: BaseMemory = None):
        if config_path is None:
            project_root = Path(__file__).parent.parent.parent
            config_path = project_root / "config.json"
        else:
            config_path = Path(config_path)

        config_dir = config_path.parent
        env_path = config_dir / ".env"
        load_dotenv(env_path)

        self.config = load_config(str(config_path))
        self.llm = get_llm(self.config)
        self.tools = self._load_tools(self.config.tools)
        self.memory = memory or get_memory("in-memory")
        self.agent = create_agent(self.llm, self.tools)
        log_event(
            logging.INFO,
            "agent.initialized",
            "OrkaAgent initialized",
            provider=self.config.llm.provider,
            model=self.config.llm.model,
            tools=self.config.tools,
        )

    def _load_tools(self, tool_names: list[str]):
        """Validate configured tool names and resolve them from the registry."""
        loaded_tools = []
        missing_tools = []

        for tool_name in tool_names:
            if not validation_manager.validate(tool_name, ToolValidator):
                raise ValueError(f"Invalid tool name in config: {tool_name!r}")
            if tool_name not in registry:
                missing_tools.append(tool_name)
                continue
            loaded_tools.append(registry[tool_name])

        if missing_tools:
            available = ", ".join(sorted(registry.keys())) or "none"
            missing = ", ".join(missing_tools)
            raise ValueError(f"Configured tool(s) not registered: {missing}. Available tools: {available}")

        return loaded_tools

    def run(self, query: str, debug: bool = False):
        """Execute a query using the agent with memory support."""
        trace = ExecutionTrace()
        trace.add_event("request.start", "Request execution started", query=query)
        log_event(
            logging.INFO,
            "request.start",
            "Request execution started",
            trace_id=trace.trace_id,
            query=query,
        )

        if not validation_manager.validate_with(query, (InputValidator, SafetyValidator)):
            trace.add_event("validation.failed", "Input validation failed", query=query)
            trace.finish()
            log_event(
                logging.WARNING,
                "validation.failed",
                "Input validation failed",
                trace_id=trace.trace_id,
                query=query,
            )
            raise ValueError("Input validation failed. Query contains invalid or unsafe content.")

        trace.add_event("validation.passed", "Input validation passed")
        log_event(logging.INFO, "validation.passed", "Input validation passed", trace_id=trace.trace_id)

        query_id = f"query_{len(self.memory.list_keys())}"
        self.memory.store(
            query_id,
            {
                "type": "query",
                "content": query,
                "timestamp": str(datetime.now()),
                "trace_id": trace.trace_id,
            },
        )
        trace.add_event("memory.store", "Stored query in memory", key=query_id)

        trace.add_event("agent.invoke", "Agent invocation started", configured_tools=self.config.tools)
        try:
            result = self.agent.invoke(query, config={"callbacks": [ToolUsageCallbackHandler(trace)]})
        except Exception as exc:
            trace.add_event("agent.error", "Agent invocation failed", error=str(exc))
            trace.finish()
            trace.add_event("request.error", "Request execution failed", duration_ms=trace.duration_ms)
            log_event(
                logging.ERROR,
                "request.error",
                "Request execution failed",
                trace_id=trace.trace_id,
                duration_ms=trace.duration_ms,
                error=str(exc),
            )
            raise

        trace.add_event("agent.result", "Agent invocation completed")

        result_id = f"{query_id}_result"
        self.memory.store(
            result_id,
            {
                "type": "result",
                "content": result,
                "timestamp": str(datetime.now()),
                "trace_id": trace.trace_id,
            },
        )
        trace.add_event("memory.store", "Stored result in memory", key=result_id)
        trace.finish()
        trace.add_event("request.end", "Request execution completed", duration_ms=trace.duration_ms)
        log_event(
            logging.INFO,
            "request.end",
            "Request execution completed",
            trace_id=trace.trace_id,
            duration_ms=trace.duration_ms,
        )

        if debug:
            return {"result": result, "trace": trace.to_dict()}
        return result
