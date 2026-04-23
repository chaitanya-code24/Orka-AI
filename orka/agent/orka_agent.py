from pydantic import BaseSettings
from langchain_groq import ChatGroq
from langchain.agents import initialize_agent, AgentType
from orka.services.crm import create_customer_tool
from orka.services.email import send_email_tool
from orka.core.logging import logger


class OrkaAgent:
    def __init__(self, config_path: str):
        class DynamicSettings(BaseSettings):
            groq_api_key: str
            model_name: str = "llama-3.3-70b-versatile"
            base_url: str = "https://api.groq.com/openai/v1"

            class Config:
                env_file = config_path

        self.settings = DynamicSettings()
        
        self.llm = ChatGroq(
            api_key=self.settings.groq_api_key,
            model_name=self.settings.model_name,
            base_url=self.settings.base_url
        )
        
        self.tools = [create_customer_tool, send_email_tool]
        
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