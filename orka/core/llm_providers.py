from orka.config.models import LLMConfig

llm_providers = {}


def register_llm_provider(provider_name: str):
    """Decorator to register an LLM provider factory function."""
    def decorator(func):
        llm_providers[provider_name] = func
        return func
    return decorator


def get_llm(llm_config: LLMConfig, api_key: str):
    """Factory function to create LLM instance based on provider."""
    provider = llm_config.provider.lower()
    if provider in llm_providers:
        return llm_providers[provider](llm_config, api_key)
    else:
        available_providers = list(llm_providers.keys())
        raise ValueError(f"Unsupported LLM provider: {llm_config.provider}. Available: {available_providers}")
