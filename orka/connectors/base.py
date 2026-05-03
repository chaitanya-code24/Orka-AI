import os
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from orka.core.exceptions import ConfigError


@dataclass(frozen=True)
class ConnectorCredentials:
    provider: str
    env_keys: list[str]
    mode: str = "demo"

    @classmethod
    def from_env(cls, provider: str, env_keys: list[str]) -> "ConnectorCredentials":
        mode = os.getenv("ORKA_CONNECTOR_MODE", "demo").lower()
        missing = [key for key in env_keys if not os.getenv(key)]
        if mode == "live" and missing:
            raise ConfigError(f"{provider} connector missing required environment variables: {', '.join(missing)}")
        return cls(provider=provider, env_keys=env_keys, mode=mode)

    @property
    def configured(self) -> bool:
        return all(os.getenv(key) for key in self.env_keys)


@dataclass(frozen=True)
class ConnectorAction:
    provider: str
    action: str
    payload: dict[str, Any]
    action_id: str = field(default_factory=lambda: f"act_{uuid4().hex[:12]}")
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ConnectorResult:
    success: bool
    provider: str
    action: str
    mode: str
    payload: dict[str, Any]
    message: str
    action_id: str
    timestamp: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class BaseConnector:
    provider = "base"
    env_keys: list[str] = []

    def __init__(self, credentials: ConnectorCredentials | None = None):
        self.credentials = credentials or ConnectorCredentials.from_env(self.provider, self.env_keys)

    def build_result(self, action: str, payload: dict[str, Any], message: str) -> dict[str, Any]:
        connector_action = ConnectorAction(provider=self.provider, action=action, payload=payload)
        result = ConnectorResult(
            success=True,
            provider=self.provider,
            action=action,
            mode=self.credentials.mode,
            payload=connector_action.payload,
            message=message,
            action_id=connector_action.action_id,
            timestamp=connector_action.timestamp,
        )
        return result.to_dict()
