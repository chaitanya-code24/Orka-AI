from collections.abc import Callable
from typing import Any


ToolCallable = Callable[..., Any]
registry: dict[str, ToolCallable] = {}


def register_tool(func: ToolCallable | None = None, *, name: str | None = None):
    """Register a callable tool by name.

    Supports both:
        @register_tool
        def my_tool(...): ...

    And:
        @register_tool(name="custom_name")
        def my_tool(...): ...
    """

    def decorator(tool_func: ToolCallable) -> ToolCallable:
        tool_name = name or tool_func.__name__
        registry[tool_name] = tool_func
        return tool_func

    if func is None:
        return decorator

    if isinstance(func, str):
        legacy_name = func

        def legacy_decorator(tool_func: ToolCallable) -> ToolCallable:
            registry[legacy_name] = tool_func
            return tool_func

        return legacy_decorator

    return decorator(func)


def get_tool(name: str) -> ToolCallable:
    try:
        return registry[name]
    except KeyError as exc:
        available = ", ".join(sorted(registry.keys())) or "none"
        raise KeyError(f"Tool '{name}' is not registered. Available tools: {available}") from exc


def list_tools() -> list[str]:
    return sorted(registry.keys())
