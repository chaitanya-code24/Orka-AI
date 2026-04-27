import json
import logging
from datetime import datetime, timezone
from typing import Any


RESERVED_LOG_FIELDS = {
    "args",
    "asctime",
    "created",
    "exc_info",
    "exc_text",
    "filename",
    "funcName",
    "levelname",
    "levelno",
    "lineno",
    "module",
    "msecs",
    "message",
    "msg",
    "name",
    "pathname",
    "process",
    "processName",
    "relativeCreated",
    "stack_info",
    "thread",
    "threadName",
}


class JSONFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "logger": record.name,
        }

        for key, value in record.__dict__.items():
            if key not in RESERVED_LOG_FIELDS and not key.startswith("_"):
                log_data[key] = value

        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_data, default=str)


def setup_logging(name: str = "orka") -> logging.Logger:
    framework_logger = logging.getLogger(name)
    framework_logger.setLevel(logging.INFO)
    framework_logger.propagate = False

    if not framework_logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(JSONFormatter())
        framework_logger.addHandler(handler)

    return framework_logger


logger = setup_logging()


def log_event(level: int, event: str, message: str, **fields: Any) -> None:
    logger.log(level, message, extra={"event": event, **fields})
