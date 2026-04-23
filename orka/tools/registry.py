from langchain.tools import tool

registry = {}


def register_tool(name: str):
    """Decorator to register a tool with the registry."""
    def decorator(func):
        # Apply LangChain's @tool decorator
        tool_obj = tool(func)
        # Register the tool
        registry[name] = tool_obj
        return tool_obj
    return decorator
