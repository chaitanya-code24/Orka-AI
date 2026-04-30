class OrkaError(Exception):
    """Base exception for all Orka framework errors."""


class ConfigError(OrkaError):
    """Raised when framework configuration is invalid."""


class GraphExecutionError(OrkaError):
    """Raised when a graph run cannot complete successfully."""


class ToolExecutionError(OrkaError):
    """Raised when a tool fails during execution."""


class ToolNotFoundError(OrkaError):
    """Raised when a requested tool is not registered."""


class ValidationError(OrkaError):
    """Raised when user input or framework state is invalid."""
