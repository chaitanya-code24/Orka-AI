from dataclasses import dataclass, field


@dataclass
class ModelConfig:
    provider: str
    model: str


@dataclass
class OrkaConfig:
    tools: list[str] = field(default_factory=list)
    model: ModelConfig | None = None
