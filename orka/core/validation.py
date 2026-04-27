from abc import ABC, abstractmethod
from typing import Any, Type


class BaseValidator(ABC):
    """Abstract base class for all validators."""

    @abstractmethod
    def validate(self, data: Any) -> bool:
        """Validate the given data. Return True if valid, False otherwise."""
        pass


class ValidationManager:
    """Manages and executes validators."""

    def __init__(self):
        self.validators: list[BaseValidator] = []

    def register_validator(self, validator: BaseValidator):
        """Register a validator instance."""
        self.validators.append(validator)

    def register_validator_class(self, validator_class: Type[BaseValidator]):
        """Register a validator class (instantiates it)."""
        self.register_validator(validator_class())

    def validate(self, data: Any, validator_type: Type[BaseValidator] = None) -> bool:
        """Validate data using all registered validators of the given type."""
        for validator in self.validators:
            if validator_type and not isinstance(validator, validator_type):
                continue
            if not validator.validate(data):
                return False
        return True


# Global validation manager
validation_manager = ValidationManager()


def register_validator(validator_class: Type[BaseValidator]):
    """Decorator to register a validator class."""
    validation_manager.register_validator_class(validator_class)
    return validator_class


# Default validators
@register_validator
class InputValidator(BaseValidator):
    """Validates user input queries."""

    def validate(self, data: str) -> bool:
        if not isinstance(data, str):
            return False
        if len(data.strip()) == 0:
            return False
        # Basic safety check - no dangerous keywords
        dangerous_words = ['delete', 'drop', 'remove', 'destroy', 'harm', 'kill', 'exploit']
        if any(word in data.lower() for word in dangerous_words):
            return False
        return True


@register_validator
class ToolValidator(BaseValidator):
    """Validates tool names and configurations."""

    def validate(self, data: str) -> bool:
        if not isinstance(data, str):
            return False
        # Check if tool name is reasonable
        if len(data) == 0 or len(data) > 100:
            return False
        # Could add more checks like allowed characters, etc.
        return True


@register_validator
class SafetyValidator(BaseValidator):
    """Additional safety validation rules."""

    def validate(self, data: str) -> bool:
        if not isinstance(data, str):
            return False
        # Check for potentially harmful patterns
        harmful_patterns = [
            'rm -rf', 'format c:', 'sudo', 'admin', 'root',
            'password', 'secret', 'token'
        ]
        if any(pattern in data.lower() for pattern in harmful_patterns):
            return False
        return True