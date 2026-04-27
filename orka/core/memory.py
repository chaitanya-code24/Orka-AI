from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class BaseMemory(ABC):
    """Abstract base class for memory systems."""

    @abstractmethod
    def store(self, key: str, value: Any) -> None:
        """Store a key-value pair in memory."""
        pass

    @abstractmethod
    def retrieve(self, key: str) -> Optional[Any]:
        """Retrieve a value by key from memory."""
        pass

    @abstractmethod
    def delete(self, key: str) -> bool:
        """Delete a key from memory. Returns True if key existed, False otherwise."""
        pass

    @abstractmethod
    def exists(self, key: str) -> bool:
        """Check if a key exists in memory."""
        pass

    @abstractmethod
    def clear(self) -> None:
        """Clear all memory."""
        pass

    @abstractmethod
    def list_keys(self) -> List[str]:
        """List all keys in memory."""
        pass


class InMemoryMemory(BaseMemory):
    """In-memory implementation of the Memory interface."""

    def __init__(self):
        """Initialize the in-memory store."""
        self._store: Dict[str, Any] = {}

    def store(self, key: str, value: Any) -> None:
        """Store a key-value pair in memory."""
        if not isinstance(key, str):
            raise TypeError("Key must be a string")
        self._store[key] = value

    def retrieve(self, key: str) -> Optional[Any]:
        """Retrieve a value by key from memory."""
        return self._store.get(key)

    def delete(self, key: str) -> bool:
        """Delete a key from memory. Returns True if key existed, False otherwise."""
        if key in self._store:
            del self._store[key]
            return True
        return False

    def exists(self, key: str) -> bool:
        """Check if a key exists in memory."""
        return key in self._store

    def clear(self) -> None:
        """Clear all memory."""
        self._store.clear()

    def list_keys(self) -> List[str]:
        """List all keys in memory."""
        return list(self._store.keys())

    def get_all(self) -> Dict[str, Any]:
        """Get all key-value pairs (InMemory-specific convenience method)."""
        return self._store.copy()


# Memory registry for pluggable implementations
memory_providers = {}


def register_memory_provider(provider_name: str):
    """Decorator to register a memory provider factory function."""
    def decorator(func):
        memory_providers[provider_name] = func
        return func
    return decorator


def get_memory(provider_name: str = "in-memory", **kwargs) -> BaseMemory:
    """Factory function to create memory instance based on provider name."""
    if provider_name not in memory_providers:
        # Default to in-memory if not registered
        if provider_name == "in-memory":
            return InMemoryMemory()
        available_providers = list(memory_providers.keys())
        raise ValueError(f"Unsupported memory provider: {provider_name}. Available: {available_providers}")
    
    return memory_providers[provider_name](**kwargs)


# Register the in-memory implementation
@register_memory_provider("in-memory")
def create_in_memory(**kwargs):
    return InMemoryMemory()
