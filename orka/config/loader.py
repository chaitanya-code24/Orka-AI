import json

from orka.config.models import ModelConfig, OrkaConfig


def load_config(config_path: str) -> OrkaConfig:
    with open(config_path, "r", encoding="utf-8-sig") as config_file:
        raw_config = json.load(config_file)

    tools = raw_config.get("tools", [])
    if not tools:
        raise ValueError("Config must define at least one tool")

    model_data = raw_config.get("model") or raw_config.get("llm")
    model = None
    if model_data:
        model = ModelConfig(
            provider=model_data["provider"],
            model=model_data["model"],
        )

    return OrkaConfig(tools=tools, model=model)
