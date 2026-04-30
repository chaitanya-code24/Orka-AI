import inspect
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from orka.core.exceptions import ToolNotFoundError, ValidationError


ToolCallable = Callable[..., Any]


@dataclass(frozen=True)
class ToolDefinition:
    name: str
    handler: ToolCallable
    description: str
    parameters: list[str]


registry: dict[str, ToolDefinition] = {}


def register_tool(func: ToolCallable | None = None, *, name: str | None = None):
    """Register a callable tool by name."""

    def decorator(tool_func: ToolCallable) -> ToolCallable:
        tool_name = name or tool_func.__name__
        signature = inspect.signature(tool_func)
        parameters = [param.name for param in signature.parameters.values()]
        registry[tool_name] = ToolDefinition(
            name=tool_name,
            handler=tool_func,
            description=inspect.getdoc(tool_func) or "",
            parameters=parameters,
        )
        return tool_func

    if func is None:
        return decorator

    if isinstance(func, str):
        legacy_name = func

        def legacy_decorator(tool_func: ToolCallable) -> ToolCallable:
            return decorator_with_name(legacy_name, tool_func)

        return legacy_decorator

    return decorator(func)


def decorator_with_name(tool_name: str, tool_func: ToolCallable) -> ToolCallable:
    signature = inspect.signature(tool_func)
    parameters = [param.name for param in signature.parameters.values()]
    registry[tool_name] = ToolDefinition(
        name=tool_name,
        handler=tool_func,
        description=inspect.getdoc(tool_func) or "",
        parameters=parameters,
    )
    return tool_func


def get_tool(name: str) -> ToolCallable:
    return get_tool_definition(name).handler


def get_tool_definition(name: str) -> ToolDefinition:
    try:
        return registry[name]
    except KeyError as exc:
        available = ", ".join(sorted(registry.keys())) or "none"
        raise ToolNotFoundError(f"Tool '{name}' is not registered. Available tools: {available}") from exc


def invoke_tool(tool_name: str, **kwargs: Any) -> Any:
    tool = get_tool_definition(tool_name)
    missing = [param for param in tool.parameters if param not in kwargs]
    if missing:
        raise ValidationError(f"Tool '{tool_name}' missing required arguments: {', '.join(missing)}")
    return tool.handler(**kwargs)


def list_tools() -> list[str]:
    return sorted(registry.keys())
