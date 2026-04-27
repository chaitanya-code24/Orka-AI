from typing import List

from pydantic import BaseModel, field_validator


class LLMConfig(BaseModel):
    provider: str
    model: str


class Config(BaseModel):
    llm: LLMConfig
    tools: List[str]

    @field_validator("tools")
    @classmethod
    def tools_must_not_be_empty(cls, tools: List[str]) -> List[str]:
        if not tools:
            raise ValueError("Config must define at least one tool")
        return tools
