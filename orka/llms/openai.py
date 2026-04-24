from langchain_openai import ChatOpenAI
from orka.core.llm_providers import register_llm_provider


class OpenAIService:
    """OpenAI LLM Service (Paid)"""

    def __init__(self, api_key: str, model: str = "gpt-4"):
        self.api_key = api_key
        self.model = model

    def get_llm(self):
        return ChatOpenAI(
            api_key=self.api_key,
            model_name=self.model
        )


@register_llm_provider("openai")
def create_openai_llm(llm_config, api_key):
    service = OpenAIService(api_key, llm_config.model)
    return service.get_llm()