import inspect
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from orka.core.exceptions import ToolNotFoundError, ValidationError


ToolCallable = Callable[..., Any]


@dataclass(frozen=True)
class ToolParameter:
    name: str
    type: str
    required: bool
    default: Any = None

    def to_schema(self) -> dict[str, Any]:
        schema: dict[str, Any] = {"type": self.type}
        if self.default is not None:
            schema["default"] = self.default
        return schema


@dataclass(frozen=True)
class ToolDefinition:
    name: str
    handler: ToolCallable
    description: str
    parameters: list[str]
    parameter_schema: list[ToolParameter]

    def to_schema(self) -> dict[str, Any]:
        properties = {parameter.name: parameter.to_schema() for parameter in self.parameter_schema}
        required = [parameter.name for parameter in self.parameter_schema if parameter.required]
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": properties,
                "required": required,
            },
        }


registry: dict[str, ToolDefinition] = {}


def register_tool(func: ToolCallable | None = None, *, name: str | None = None):
    """Register a callable tool by name."""

    def decorator(tool_func: ToolCallable) -> ToolCallable:
        tool_name = name or tool_func.__name__
        registry[tool_name] = _build_tool_definition(tool_name, tool_func)
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
    registry[tool_name] = _build_tool_definition(tool_name, tool_func)
    return tool_func


def _build_tool_definition(tool_name: str, tool_func: ToolCallable) -> ToolDefinition:
    signature = inspect.signature(tool_func)
    parameter_schema = [_build_parameter_schema(param) for param in signature.parameters.values()]
    parameters = [param.name for param in parameter_schema]
    return ToolDefinition(
        name=tool_name,
        handler=tool_func,
        description=inspect.getdoc(tool_func) or "",
        parameters=parameters,
        parameter_schema=parameter_schema,
    )


def _build_parameter_schema(parameter: inspect.Parameter) -> ToolParameter:
    return ToolParameter(
        name=parameter.name,
        type=_annotation_to_json_type(parameter.annotation),
        required=parameter.default is inspect.Parameter.empty,
        default=None if parameter.default is inspect.Parameter.empty else parameter.default,
    )


def _annotation_to_json_type(annotation: Any) -> str:
    if annotation is inspect.Parameter.empty:
        return "string"
    if annotation is str:
        return "string"
    if annotation is int:
        return "integer"
    if annotation is float:
        return "number"
    if annotation is bool:
        return "boolean"
    if annotation in {dict, list}:
        return annotation.__name__
    return "string"


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
    missing = [param.name for param in tool.parameter_schema if param.required and param.name not in kwargs]
    if missing:
        raise ValidationError(f"Tool '{tool_name}' missing required arguments: {', '.join(missing)}")
    unknown = sorted(set(kwargs) - set(tool.parameters))
    if unknown:
        raise ValidationError(f"Tool '{tool_name}' received unknown arguments: {', '.join(unknown)}")
    _validate_argument_types(tool, kwargs)
    return tool.handler(**kwargs)


def list_tools() -> list[str]:
    return sorted(registry.keys())


def list_tool_schemas() -> list[dict[str, Any]]:
    return [get_tool_definition(tool_name).to_schema() for tool_name in list_tools()]


def _validate_argument_types(tool: ToolDefinition, kwargs: dict[str, Any]) -> None:
    for parameter in tool.parameter_schema:
        if parameter.name not in kwargs:
            continue
        value = kwargs[parameter.name]
        if not _matches_json_type(value, parameter.type):
            raise ValidationError(
                f"Tool '{tool.name}' argument '{parameter.name}' expected {parameter.type}, "
                f"got {type(value).__name__}"
            )


def _matches_json_type(value: Any, json_type: str) -> bool:
    if json_type == "string":
        return isinstance(value, str)
    if json_type == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if json_type == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    if json_type == "boolean":
        return isinstance(value, bool)
    if json_type == "dict":
        return isinstance(value, dict)
    if json_type == "list":
        return isinstance(value, list)
    return True
