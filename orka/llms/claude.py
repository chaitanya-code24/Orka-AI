from langchain_anthropic import ChatAnthropic
from orka.core.llm_providers import register_llm_provider


class ClaudeService:
    """Anthropic Claude LLM Service (Paid)"""

    def __init__(self, api_key: str, model: str = "claude-3-sonnet-20240229"):
        self.api_key = api_key
        self.model = model

    def get_llm(self):
        return ChatAnthropic(
            api_key=self.api_key,
            model_name=self.model
        )


@register_llm_provider("claude")
def create_claude_llm(llm_config, api_key):
    service = ClaudeService(api_key, llm_config.model)
    return service.get_llm()