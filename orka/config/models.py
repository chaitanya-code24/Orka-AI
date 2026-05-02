from dataclasses import dataclass, field


@dataclass
class ModelConfig:
    provider: str
    model: str


@dataclass
class OrkaConfig:
    tools: list[str] = field(default_factory=list)
    model: ModelConfig | None = None
    version: str = "1"
    environment: str = "development"
    storage_path: str = "orka.db"
    approval_required_tools: list[str] = field(default_factory=list)


# Compatibility aliases for older internal modules that still import these names.
LLMConfig = ModelConfig


@dataclass
class Config:
    llm: ModelConfig
    tools: list[str] = field(default_factory=list)
