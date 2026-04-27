import os
from typing import Union

from orka.config.models import Config, LLMConfig
from orka.core.llm_providers import get_llm as get_provider_llm

# Import provider modules so their registration decorators run.
import orka.llms  # noqa: F401


PROVIDER_API_KEYS = {
    "groq": "GROQ_API_KEY",
    "openai": "OPENAI_API_KEY",
    "gemini": "GOOGLE_API_KEY",
    "claude": "ANTHROPIC_API_KEY",
}


def get_llm(config: Union[Config, LLMConfig]):
    """Create an LLM from framework config without exposing provider internals."""
    llm_config = config.llm if isinstance(config, Config) else config
    provider = llm_config.provider.lower()

    api_key_name = PROVIDER_API_KEYS.get(provider)
    if not api_key_name:
        raise ValueError(f"Unsupported provider '{llm_config.provider}' in config")

    api_key = os.getenv(api_key_name)
    if not api_key or api_key.startswith("your_"):
        raise ValueError(f"{api_key_name} not set in .env file. Please provide a valid API key.")

    return get_provider_llm(llm_config, api_key)
