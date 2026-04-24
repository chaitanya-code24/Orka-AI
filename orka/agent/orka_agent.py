import os
from pathlib import Path
from dotenv import load_dotenv
from langchain.agents import initialize_agent, AgentType
from orka.config.loader import load_config
from orka.tools.registry import registry
from orka.core.logging import logger
from orka.core.llm import get_llm

class OrkaAgent:
    def __init__(self, config_path: str):
        config_dir = Path(config_path).parent
        env_path = config_dir / ".env"
        load_dotenv(env_path)
        
        self.config = load_config(config_path)
        
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY not found in .env")
        
        self.llm = get_llm(self.config.llm, api_key)
        
        self.tools = [registry[name] for name in self.config.tools]
        
        self.agent = initialize_agent(
            self.tools,
            self.llm,
            agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            verbose=True
        )

    def run(self, query: str):
        logger.info(f"Executing query: {query}")
        result = self.agent.run(query)
        return result
