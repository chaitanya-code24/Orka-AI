from abc import ABC, abstractmethod
from typing import Any

from orka.core.storage import SQLiteStorage


class BaseRunStore(ABC):
    @abstractmethod
    def save_run(self, run_id: str, payload: dict[str, Any]) -> None:
        pass

    @abstractmethod
    def get_run(self, run_id: str) -> dict[str, Any] | None:
        pass

    @abstractmethod
    def list_runs(self) -> list[dict[str, Any]]:
        pass


class InMemoryRunStore(BaseRunStore):
    def __init__(self):
        self._runs: dict[str, dict[str, Any]] = {}

    def save_run(self, run_id: str, payload: dict[str, Any]) -> None:
        self._runs[run_id] = payload

    def get_run(self, run_id: str) -> dict[str, Any] | None:
        return self._runs.get(run_id)

    def list_runs(self) -> list[dict[str, Any]]:
        return list(self._runs.values())


class SQLiteRunStore(BaseRunStore):
    def __init__(self, storage: SQLiteStorage):
        self.storage = storage

    def save_run(self, run_id: str, payload: dict[str, Any]) -> None:
        self.storage.save_run(run_id, payload)

    def get_run(self, run_id: str) -> dict[str, Any] | None:
        return self.storage.get_run(run_id)

    def list_runs(self) -> list[dict[str, Any]]:
        return self.storage.list_runs()
