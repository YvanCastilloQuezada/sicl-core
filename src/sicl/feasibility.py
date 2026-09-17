from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import Enum
from math import isclose
from typing import Any, Iterable, Mapping


class FeasibilityState(str, Enum):
    FEASIBLE = "FEASIBLE"
    INFEASIBLE = "INFEASIBLE"
    UNKNOWN = "UNKNOWN"
    INSUFFICIENT_DATA = "INSUFFICIENT_DATA"


class VariableType(str, Enum):
    OBJECTIVE = "OBJECTIVE"
    CONSTRAINT = "CONSTRAINT"
    PARAMETER = "PARAMETER"


@dataclass(frozen=True)
class SuggestedVariable:
    suggestion_id: str
    normalized_key: str
    label: str
    variable_type: VariableType
    spatial_scope: str
    normative_reference: str | None = None
    canonical_variable_id: str | None = None
    catalog_version: str | None = None
    definition_version: str | None = None
    profile_version: str | None = None


@dataclass(frozen=True)
class ProjectVariable:
    variable_id: str
    project_id: str
    normalized_key: str
    variable_type: VariableType
    value: Any
    actor_id: str
    authority: str
    unit: str | None = None
    spatial_scope: str = "edificacion"
    source: str = "USER_INPUT"
    version: int = 1
    supersedes_variable_id: str | None = None
    normative_reference: str | None = None
    canonical_variable_id: str | None = None
    catalog_version: str | None = None
    definition_version: str | None = None
    profile_version: str | None = None

    def __post_init__(self) -> None:
        if not all((self.variable_id, self.project_id, self.normalized_key, self.actor_id, self.authority)):
            raise ValueError("ProjectVariable requires id, project, key, actor_id and authority")


@dataclass(frozen=True)
class ConstraintCheck:
    constraint_id: str
    key: str
    state: str
    hard: bool
    actual: Any = None
    expected: float | None = None
    operator: str | None = None
    reason: str | None = None


@dataclass(frozen=True)
class FeasibilityResult:
    alternative_id: str
    state: FeasibilityState
    checks: tuple[ConstraintCheck, ...]
    failed_constraint_ids: tuple[str, ...]
    unknown_constraint_ids: tuple[str, ...]
    insufficient_constraint_ids: tuple[str, ...]
    evidence_ids: tuple[str, ...]
    assumption_ids: tuple[str, ...]
    evaluated_by: str
    method: str = "constraint_filter_v1"

    def to_dict(self) -> dict[str, Any]:
        result = asdict(self)
        result["state"] = self.state.value
        result["checks"] = [asdict(check) for check in self.checks]
        for key in ("failed_constraint_ids", "unknown_constraint_ids", "insufficient_constraint_ids", "evidence_ids", "assumption_ids"):
            result[key] = list(result[key])
        return result


def normalized_key(value: str) -> str:
    return "_".join(value.strip().upper().replace("-", "_").split())


def project_variable_dict(value: ProjectVariable | SuggestedVariable) -> dict[str, Any]:
    result = asdict(value)
    result["variable_type"] = value.variable_type.value
    return result


def _compare(actual: float, operator: str, expected: float) -> bool:
    if operator == "<=": return actual <= expected
    if operator == "<": return actual < expected
    if operator == "=": return isclose(actual, expected, rel_tol=1e-9, abs_tol=1e-9)
    if operator == ">=": return actual >= expected
    if operator == ">": return actual > expected
    raise ValueError(f"unsupported operator: {operator}")


def evaluate_feasibility(alternative_id: str, values: Mapping[str, Any], constraints: Iterable[Mapping[str, Any]], *, evaluated_by: str = "system-feasibility") -> FeasibilityResult:
    checks: list[ConstraintCheck] = []
    for constraint in constraints:
        cid = str(constraint["constraint_id"])
        key = normalized_key(str(constraint["key"]))
        hard = bool(constraint.get("hard", True))
        expected = float(constraint["value"])
        operator = str(constraint["operator"])
        actual = values.get(key, values.get(str(constraint["key"])))
        if actual is None:
            checks.append(ConstraintCheck(cid, key, "INSUFFICIENT_DATA", hard, expected=expected, operator=operator, reason="required value is absent"))
            continue
        try:
            numeric = float(actual)
            state = "SATISFIED" if _compare(numeric, operator, expected) else "VIOLATED"
            checks.append(ConstraintCheck(cid, key, state, hard, actual=numeric, expected=expected, operator=operator))
        except (TypeError, ValueError) as exc:
            checks.append(ConstraintCheck(cid, key, "UNKNOWN", hard, actual=actual, expected=expected, operator=operator, reason=str(exc)))
    failed = tuple(check.constraint_id for check in checks if check.hard and check.state == "VIOLATED")
    unknown = tuple(check.constraint_id for check in checks if check.state == "UNKNOWN")
    insufficient = tuple(check.constraint_id for check in checks if check.state == "INSUFFICIENT_DATA")
    state = FeasibilityState.INFEASIBLE if failed else FeasibilityState.UNKNOWN if unknown else FeasibilityState.INSUFFICIENT_DATA if insufficient else FeasibilityState.FEASIBLE
    return FeasibilityResult(alternative_id, state, tuple(checks), failed, unknown, insufficient, tuple(), tuple(), evaluated_by)


def serialize_result(result: FeasibilityResult) -> dict[str, Any]:
    return result.to_dict()


def feasible_pareto_front(pareto_front: Iterable[str], results: Iterable[FeasibilityResult]) -> list[str]:
    feasible = {result.alternative_id for result in results if result.state is FeasibilityState.FEASIBLE}
    return [alternative_id for alternative_id in pareto_front if alternative_id in feasible]


def validate_project_variable_uniqueness(existing: Iterable[ProjectVariable], candidate: ProjectVariable) -> None:
    if any(item.project_id == candidate.project_id and item.normalized_key == candidate.normalized_key for item in existing):
        raise ValueError(f"duplicate project variable key: {candidate.project_id}:{candidate.normalized_key}")


__all__ = ["FeasibilityState", "VariableType", "SuggestedVariable", "ProjectVariable", "ConstraintCheck", "FeasibilityResult", "normalized_key", "project_variable_dict", "evaluate_feasibility", "serialize_result", "feasible_pareto_front", "validate_project_variable_uniqueness"]
