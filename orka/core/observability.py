import logging
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Optional
from uuid import uuid4

from orka.core.logging import log_event

try:
    from langchain_core.callbacks import BaseCallbackHandler
except ImportError:  # pragma: no cover - keeps observability importable without LangChain.
    BaseCallbackHandler = object


@dataclass
class TraceEvent:
    event: str
    message: str
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "event": self.event,
            "message": self.message,
            "timestamp": self.timestamp,
            "metadata": self.metadata,
        }


@dataclass
class ExecutionTrace:
    trace_id: str = field(default_factory=lambda: str(uuid4()))
    started_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    events: list[TraceEvent] = field(default_factory=list)
    completed_at: Optional[str] = None
    duration_ms: Optional[float] = None
    _start_time: float = field(default_factory=time.perf_counter, repr=False)

    def add_event(self, event: str, message: str, **metadata: Any) -> None:
        self.events.append(TraceEvent(event=event, message=message, metadata=metadata))

    def finish(self) -> None:
        self.completed_at = datetime.now(timezone.utc).isoformat()
        self.duration_ms = round((time.perf_counter() - self._start_time) * 1000, 2)

    def to_dict(self) -> dict[str, Any]:
        return {
            "trace_id": self.trace_id,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "duration_ms": self.duration_ms,
            "events": [event.to_dict() for event in self.events],
        }


class ToolUsageCallbackHandler(BaseCallbackHandler):
    def __init__(self, trace: ExecutionTrace):
        self.trace = trace

    def on_tool_start(self, serialized: dict[str, Any], input_str: str, **kwargs: Any) -> None:
        tool_name = serialized.get("name") or serialized.get("id") or "unknown_tool"
        self.trace.add_event("tool.start", "Tool execution started", tool_name=tool_name, input=input_str)
        log_event(
            logging.INFO,
            "tool.start",
            "Tool execution started",
            trace_id=self.trace.trace_id,
            tool_name=tool_name,
        )

    def on_tool_end(self, output: Any, **kwargs: Any) -> None:
        self.trace.add_event("tool.end", "Tool execution completed", output=str(output))
        log_event(
            logging.INFO,
            "tool.end",
            "Tool execution completed",
            trace_id=self.trace.trace_id,
        )

    def on_tool_error(self, error: BaseException, **kwargs: Any) -> None:
        self.trace.add_event("tool.error", "Tool execution failed", error=str(error))
        log_event(
            logging.ERROR,
            "tool.error",
            "Tool execution failed",
            trace_id=self.trace.trace_id,
            error=str(error),
        )
