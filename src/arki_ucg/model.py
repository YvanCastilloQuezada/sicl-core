"""
ARKI Universal Command Generator (UCG)
UCG-00C: Consolidated foundational semantic model.

L1-L8 define command semantic identity.
Parameters and context are independent from identity.
This module defines no executor and grants no capability.
"""

from dataclasses import dataclass, field
from typing import Any, Mapping, Optional, Tuple

from .immutable import freeze, thaw
from .normalization import normalize_semantic_text


COMMAND_SCHEMA = "arki.ucg.command.v1"

LEVELS = (
    "L1_domain",
    "L2_family",
    "L3_intent",
    "L4_operation",
    "L5_entity",
    "L6_type",
    "L7_mode",
    "L8_output",
)

CODE_LENGTH = 8


@dataclass(frozen=True)
class ValidationIssue:
    code: str
    message: str
    level: Optional[str] = None


@dataclass(frozen=True)
class ValidationResult:
    valid: bool
    issues: Tuple[ValidationIssue, ...] = ()

    @property
    def errors(self):
        return self.issues

    @classmethod
    def success(cls):
        return cls(valid=True, issues=())

    @classmethod
    def failure(cls, *issues):
        return cls(valid=False, issues=tuple(issues))


@dataclass(frozen=True)
class CommandParameters:
    """
    Runtime parameters.
    Parameters do not define command semantic identity.
    """
    values: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        object.__setattr__(self, "values", freeze(self.values))


@dataclass(frozen=True)
class CommandContext:
    """
    Runtime context, independent from command identity.

    Explicit fields cover common ARKI context dimensions.
    Additional context may be carried in values.
    """
    project_id: Optional[str] = None
    lifecycle_phase: Optional[str] = None
    scale: Optional[str] = None
    selection: Optional[str] = None
    values: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        object.__setattr__(self, "values", freeze(self.values))


@dataclass(frozen=True)
class CommandDefinition:
    """
    Semantic command definition composed of exactly eight levels.

    Incomplete definitions may exist during composition.
    Incomplete definitions are not executable.
    No executor or capability is implied by this object.
    """
    L1_domain: Optional[str] = None
    L2_family: Optional[str] = None
    L3_intent: Optional[str] = None
    L4_operation: Optional[str] = None
    L5_entity: Optional[str] = None
    L6_type: Optional[str] = None
    L7_mode: Optional[str] = None
    L8_output: Optional[str] = None

    parameters: CommandParameters = field(
        default_factory=CommandParameters
    )
    context: CommandContext = field(
        default_factory=CommandContext
    )

    @property
    def level_values(self) -> Tuple[Optional[str], ...]:
        return tuple(getattr(self, level) for level in LEVELS)

    @property
    def is_complete(self) -> bool:
        return all(
            isinstance(value, str) and bool(value.strip())
            for value in self.level_values
        )

    @property
    def semantic_tuple(self) -> Tuple[str, ...]:
        if not self.is_complete:
            raise ValueError("Command definition is incomplete.")
        return tuple(
            normalize_semantic_text(value)
            for value in self.level_values
        )

    @property
    def semantic_identity(self) -> Tuple[str, ...]:
        return self.semantic_tuple

    def to_dict(self) -> dict:
        return {
            "schema": COMMAND_SCHEMA,
            "levels": {
                level: getattr(self, level)
                for level in LEVELS
            },
            "parameters": thaw(self.parameters.values),
            "context": {
                "project_id": self.context.project_id,
                "lifecycle_phase": self.context.lifecycle_phase,
                "scale": self.context.scale,
                "selection": self.context.selection,
                "values": thaw(self.context.values),
            },
            "complete": self.is_complete,
        }


def validate_definition(
    definition: CommandDefinition,
) -> ValidationResult:
    issues = []

    if not isinstance(definition, CommandDefinition):
        return ValidationResult.failure(
            ValidationIssue(
                code="DEFINITION_TYPE_INVALID",
                message="Expected CommandDefinition.",
            )
        )

    for level in LEVELS:
        value = getattr(definition, level)

        if value is None:
            issues.append(
                ValidationIssue(
                    code="LEVEL_MISSING",
                    message=f"{level} is missing.",
                    level=level,
                )
            )
        elif not isinstance(value, str):
            issues.append(
                ValidationIssue(
                    code="LEVEL_TYPE_INVALID",
                message=f"{level} must be a string.",
                    level=level,
                )
            )
        elif not value.strip():
            issues.append(
                ValidationIssue(
                    code="LEVEL_EMPTY",
                    message=f"{level} cannot be empty.",
                    level=level,
                )
            )

    if not isinstance(definition.parameters, CommandParameters):
        issues.append(
            ValidationIssue(
                code="PARAMETERS_CONTAINER_INVALID",
                message="parameters must be CommandParameters.",
            )
        )
    elif not isinstance(definition.parameters.values, Mapping):
        issues.append(
            ValidationIssue(
                code="PARAMETERS_INVALID",
                message="parameters.values must be a mapping.",
            )
        )

    if not isinstance(definition.context, CommandContext):
        issues.append(
            ValidationIssue(
                code="CONTEXT_CONTAINER_INVALID",
                message="context must be CommandContext.",
            )
        )
    elif not isinstance(definition.context.values, Mapping):
        issues.append(
            ValidationIssue(
                code="CONTEXT_INVALID",
                message="context.values must be a mapping.",
            )
        )

    if issues:
        return ValidationResult.failure(*issues)

    return ValidationResult.success()
