from langchain_groq import ChatGroq
from orka.core.llm_providers import register_llm_provider


class GroqService:
    """Groq LLM Service (Free)"""

    def __init__(self, api_key: str, model: str = "llama-3.3-70b-versatile"):
        self.api_key = api_key
        self.model = model

    def get_llm(self):
        return ChatGroq(
            api_key=self.api_key,
            model_name=self.model,
            base_url="https://api.groq.com/openai/v1"
        )


@register_llm_provider("groq")
def create_groq_llm(llm_config, api_key):
    service = GroqService(api_key, llm_config.model)
    return service.get_llm()