import json
from .models import Config

def load_config(config_path: str) -> Config:
    with open(config_path, 'r') as f:
        data = json.load(f)
    return Config(**data)
