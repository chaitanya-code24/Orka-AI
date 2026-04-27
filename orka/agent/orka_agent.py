from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from langchain.agents import create_agent

from orka.config.loader import load_config
from orka.core.llm import get_llm
from orka.core.logging import logger
from orka.core.memory import BaseMemory, get_memory
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

    def run(self, query: str):
        """Execute a query using the agent with memory support."""
        if not validation_manager.validate_with(query, (InputValidator, SafetyValidator)):
            logger.warning(f"Input validation failed for query: {query}")
            raise ValueError("Input validation failed. Query contains invalid or unsafe content.")

        logger.info(f"Executing query: {query}")

        query_id = f"query_{len(self.memory.list_keys())}"
        self.memory.store(
            query_id,
            {
                "type": "query",
                "content": query,
                "timestamp": str(datetime.now()),
            },
        )

        result = self.agent.invoke(query)

        result_id = f"{query_id}_result"
        self.memory.store(
            result_id,
            {
                "type": "result",
                "content": result,
                "timestamp": str(datetime.now()),
            },
        )

        return result
