import json

from orka.config.models import Config


def load_config(config_path: str) -> Config:
    with open(config_path, "r", encoding="utf-8-sig") as f:
        data = json.load(f)
    return Config(**data)
