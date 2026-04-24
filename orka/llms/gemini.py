from langchain_google_genai import ChatGoogleGenerativeAI
from orka.core.llm_providers import register_llm_provider


class GeminiService:
    """Google Gemini LLM Service (Free)"""

    def __init__(self, api_key: str, model: str = "gemini-1.5-pro"):
        self.api_key = api_key
        self.model = model

    def get_llm(self):
        return ChatGoogleGenerativeAI(
            api_key=self.api_key,
            model=self.model
        )


@register_llm_provider("gemini")
def create_gemini_llm(llm_config, api_key):
    service = GeminiService(api_key, llm_config.model)
    return service.get_llm()