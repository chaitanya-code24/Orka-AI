import json

from orka.config.models import ModelConfig, OrkaConfig
from orka.core.exceptions import ConfigError


def load_config(config_path: str) -> OrkaConfig:
    try:
        with open(config_path, "r", encoding="utf-8-sig") as config_file:
            raw_config = json.load(config_file)
    except FileNotFoundError as exc:
        raise ConfigError(f"Config file not found: {config_path}") from exc
    except json.JSONDecodeError as exc:
        raise ConfigError(f"Invalid JSON in config file: {config_path}") from exc

    tools = raw_config.get("tools", [])
    if not isinstance(tools, list) or not tools or not all(isinstance(tool, str) and tool.strip() for tool in tools):
        raise ConfigError("Config must define a non-empty 'tools' list of tool names")

    approval_required_tools = raw_config.get("approval_required_tools", [])
    if not isinstance(approval_required_tools, list) or not all(
        isinstance(tool, str) and tool.strip() for tool in approval_required_tools
    ):
        raise ConfigError("'approval_required_tools' must be a list of tool names when provided")

    model_data = raw_config.get("model") or raw_config.get("llm")
    model = None
    if model_data:
        if not isinstance(model_data, dict):
            raise ConfigError("'model' must be an object when provided")
        provider = model_data.get("provider")
        model_name = model_data.get("model")
        if not provider or not model_name:
            raise ConfigError("'model' must include 'provider' and 'model'")
        model = ModelConfig(provider=provider, model=model_name)

    version = str(raw_config.get("version", "1"))
    environment = str(raw_config.get("environment", "development"))
    storage_path = str(raw_config.get("storage_path", "orka.db"))
    return OrkaConfig(
        tools=tools,
        model=model,
        version=version,
        environment=environment,
        storage_path=storage_path,
        approval_required_tools=approval_required_tools,
    )
