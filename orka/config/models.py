from pydantic import BaseModel
from typing import List

class LLMConfig(BaseModel):
    provider: str
    model: str

class Config(BaseModel):
    llm: LLMConfig
    tools: List[str]
