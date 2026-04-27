import os
from pathlib import Path
from dotenv import load_dotenv
from langchain.agents import create_agent
from orka.config.loader import load_config
from orka.core.logging import logger
from orka.core.llm_providers import get_llm
from orka.core.memory import BaseMemory, get_memory
from orka.core.validation import validation_manager, InputValidator
from orka.tools.registry import registry

class OrkaAgent:
    def __init__(self, config_path: str = None, memory: BaseMemory = None):
        if config_path is None:
            # Default to config.json in the project root
            project_root = Path(__file__).parent.parent.parent
            config_path = project_root / "config.json"
        else:
            config_path = Path(config_path)
        
        config_dir = config_path.parent
        env_path = config_dir / ".env"
        load_dotenv(env_path)
        
        self.config = load_config(str(config_path))

        provider_api_keys = {
            "groq": "GROQ_API_KEY",
            "openai": "OPENAI_API_KEY",
            "gemini": "GOOGLE_API_KEY",
            "claude": "ANTHROPIC_API_KEY",
        }

        api_key_name = provider_api_keys.get(self.config.llm.provider.lower())
        if not api_key_name:
            raise ValueError(f"Unsupported provider '{self.config.llm.provider}' in config.json")

        api_key = os.getenv(api_key_name)
        if not api_key or api_key.startswith("your_"):
            raise ValueError(f"{api_key_name} not set in .env file. Please provide a valid API key.")

        self.llm = get_llm(self.config.llm, api_key)
        
        self.tools = [registry[name] for name in self.config.tools]
        
        # Initialize memory (default to in-memory if not provided)
        self.memory = memory or get_memory("in-memory")
        
        # Create the agent with the selected model and tools
        self.agent = create_agent(self.llm, self.tools)

    def run(self, query: str):
        """Execute a query using the agent with memory support."""
        # Validate input
        if not validation_manager.validate(query, InputValidator):
            logger.warning(f"Input validation failed for query: {query}")
            raise ValueError("Input validation failed. Query contains invalid or unsafe content.")
        
        logger.info(f"Executing query: {query}")
        
        # Store query in memory
        query_id = f"query_{len(self.memory.list_keys())}"
        self.memory.store(query_id, {
            "type": "query",
            "content": query,
            "timestamp": str(__import__('datetime').datetime.now())
        })
        
        # Execute the agent
        result = self.agent.invoke(query)
        
        # Store result in memory
        result_id = f"{query_id}_result"
        self.memory.store(result_id, {
            "type": "result",
            "content": result,
            "timestamp": str(__import__('datetime').datetime.now())
        })
        
        return result
