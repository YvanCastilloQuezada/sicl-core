"""
ARKI Universal Command Generator (UCG).
UCG-00C consolidated semantic foundation.
No executor or capability is implied.
"""

from .model import (
    COMMAND_SCHEMA,
    LEVELS,
    CODE_LENGTH,
    ValidationIssue,
    ValidationResult,
    CommandParameters,
    CommandContext,
    CommandDefinition,
    validate_definition,
)

__all__ = [
    "COMMAND_SCHEMA",
    "LEVELS",
    "CODE_LENGTH",
    "ValidationIssue",
    "ValidationResult",
    "CommandParameters",
    "CommandContext",
    "CommandDefinition",
    "validate_definition",
]
