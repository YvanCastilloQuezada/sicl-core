"""ARKI H-004: Reaction Planning — read-only planning of responses.

H-004 consume un ValidityReport de H-003 y produce un ReactionPlan.
NO ejecuta, recomputa, notifica ni muta: solo planifica.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from .derivation import VersionedRef
from .validity import ValidityReport, ArtifactValidity

_BLOCKED_PRIORITY = 999
_REFERENCE_KEYS = frozenset(("entityType", "entityId", "version"))


class ActionType(str, Enum):
    RECOMPUTE = "RECOMPUTE"
    REVIEW = "REVIEW"
    REJECT = "REJECT"
    ESCALATE = "ESCALATE"


class ActionStatus(str, Enum):
    PLANNED = "PLANNED"
    BLOCKED = "BLOCKED"
    REQUIRES_AUTHORITY = "REQUIRES_AUTHORITY"


@dataclass(frozen=True)
class PlannedAction:
    artifact_ref: VersionedRef
    action_type: ActionType
    status: ActionStatus
    priority: int
    reason: str
    requires_human_authority: bool
    blocked_by: tuple[VersionedRef, ...] = field(default_factory=tuple)

    def to_dict(self) -> dict[str, Any]:
        return {
            "artifactRef": self.artifact_ref.to_dict(),
            "actionType": self.action_type.value,
            "status": self.status.value,
            "priority": self.priority,
            "reason": self.reason,
            "requiresHumanAuthority": self.requires_human_authority,
            "blockedBy": [ref.to_dict() for ref in self.blocked_by],
        }


@dataclass(frozen=True)
class ReactionPlan:
    validity_report: ValidityReport
    contract_version: int = 1
    planned_actions: tuple[PlannedAction, ...] = field(default_factory=tuple)
    analysis_metadata: dict[str, int] = field(default_factory=dict)
    read_only: bool = True

    def to_dict(self) -> dict[str, Any]:
        return {
            "contractVersion": self.contract_version,
            "validityReport": self.validity_report.to_dict(),
            "plannedActions": [a.to_dict() for a in self.planned_actions],
            "analysisMetadata": self.analysis_metadata,
            "readOnly": self.read_only,
        }


class ReactionPlanner:
    """H-004: transforma estados de validez en acciones planificadas.

    Política explícita: FULLY_STALE se planifica como RECOMPUTE sin
    autorización humana adicional; los estados inciertos, inválidos,
    parciales y discrepancias malformadas sí escalan a revisión.
    """

    def plan_reaction(self, validity_report: ValidityReport) -> ReactionPlan:
        actions = [
            action
            for artifact_validity in validity_report.artifact_validities
            if (action := self._determine_action(artifact_validity)) is not None
        ]
        ordered_actions = self._topological_sort(actions, validity_report)
        metadata = {
            "totalActionsPlanned": len(ordered_actions),
            "recomputeCount": sum(a.action_type == ActionType.RECOMPUTE for a in ordered_actions),
            "reviewCount": sum(a.action_type == ActionType.REVIEW for a in ordered_actions),
            "rejectCount": sum(a.action_type == ActionType.REJECT for a in ordered_actions),
            "escalateCount": sum(a.action_type == ActionType.ESCALATE for a in ordered_actions),
            "requiresAuthorityCount": sum(a.requires_human_authority for a in ordered_actions),
        }
        return ReactionPlan(
            validity_report=validity_report,
            planned_actions=tuple(ordered_actions),
            analysis_metadata=metadata,
            read_only=True,
        )

    def _determine_action(self, artifact_validity: ArtifactValidity) -> PlannedAction | None:
        state = artifact_validity.state
        if any(self._is_malformed_discrepancy(discrepancy)
               for derivation in artifact_validity.derivation_validities
               for discrepancy in derivation.discrepancies):
            return PlannedAction(
                artifact_ref=artifact_validity.artifact_ref,
                action_type=ActionType.ESCALATE,
                status=ActionStatus.BLOCKED,
                priority=_BLOCKED_PRIORITY,
                reason="MALFORMED_DISCREPANCY",
                requires_human_authority=True,
            )
        if state == "FULLY_VALID":
            return None
        if state == "PARTIALLY_VALID":
            return PlannedAction(
                artifact_ref=artifact_validity.artifact_ref,
                action_type=ActionType.REVIEW,
                status=ActionStatus.REQUIRES_AUTHORITY,
                priority=0,
                reason="At least one derivation is valid, but others are stale",
                requires_human_authority=True,
            )
        if state == "FULLY_STALE":
            return PlannedAction(
                artifact_ref=artifact_validity.artifact_ref,
                action_type=ActionType.RECOMPUTE,
                status=ActionStatus.PLANNED,
                priority=0,
                reason="All derivations are stale",
                requires_human_authority=False,
            )
        if state == "PARTIALLY_STALE":
            return PlannedAction(
                artifact_ref=artifact_validity.artifact_ref,
                action_type=ActionType.REVIEW,
                status=ActionStatus.REQUIRES_AUTHORITY,
                priority=0,
                reason="Some derivations are stale",
                requires_human_authority=True,
            )
        if state == "REQUIRES_HUMAN_REVIEW":
            return PlannedAction(
                artifact_ref=artifact_validity.artifact_ref,
                action_type=ActionType.ESCALATE,
                status=ActionStatus.REQUIRES_AUTHORITY,
                priority=0,
                reason="Identity uncertainty or invalid dependencies detected",
                requires_human_authority=True,
            )
        if state == "INVALID":
            return PlannedAction(
                artifact_ref=artifact_validity.artifact_ref,
                action_type=ActionType.REJECT,
                status=ActionStatus.REQUIRES_AUTHORITY,
                priority=0,
                reason="Invalid dependency detected",
                requires_human_authority=True,
            )
        return None

    def _topological_sort(
        self,
        actions: list[PlannedAction],
        validity_report: ValidityReport,
    ) -> list[PlannedAction]:
        if not actions:
            return []

        action_by_ref = {action.artifact_ref: action for action in actions}
        dependencies: dict[VersionedRef, set[VersionedRef]] = {
            action.artifact_ref: set() for action in actions
        }
        for artifact_validity in validity_report.artifact_validities:
            output = artifact_validity.artifact_ref
            if output not in action_by_ref:
                continue
            for derivation_validity in artifact_validity.derivation_validities:
                for discrepancy in derivation_validity.discrepancies:
                    raw = discrepancy.get("reference", {})
                    if not isinstance(raw, dict) or not _REFERENCE_KEYS.issubset(raw):
                        continue
                    dependency = VersionedRef(
                        raw["entityType"], raw["entityId"], raw["version"]
                    )
                    if dependency in action_by_ref and dependency != output:
                        dependencies[output].add(dependency)

        # Kahn: an action is ready when all action-producing dependencies are ready.
        dependents: dict[VersionedRef, set[VersionedRef]] = {
            ref: set() for ref in dependencies
        }
        in_degree = {ref: len(deps) for ref, deps in dependencies.items()}
        for output, deps in dependencies.items():
            for dependency in deps:
                dependents[dependency].add(output)

        queue = sorted(
            (ref for ref, degree in in_degree.items() if degree == 0),
            key=lambda ref: (ref.entity_type, ref.entity_id, ref.version),
        )
        ordered_refs: list[VersionedRef] = []
        while queue:
            current = queue.pop(0)
            ordered_refs.append(current)
            for dependent in sorted(
                dependents[current], key=lambda ref: (ref.entity_type, ref.entity_id, ref.version)
            ):
                in_degree[dependent] -= 1
                if in_degree[dependent] == 0:
                    queue.append(dependent)
            queue.sort(key=lambda ref: (ref.entity_type, ref.entity_id, ref.version))

        if len(ordered_refs) != len(actions):
            cycle_refs = set(dependencies) - set(ordered_refs)
            for ref in sorted(cycle_refs, key=lambda ref: (ref.entity_type, ref.entity_id, ref.version)):
                ordered_refs.append(ref)

        result: list[PlannedAction] = []
        unresolved = {ref for ref, degree in in_degree.items() if degree > 0}
        for priority, ref in enumerate(ordered_refs):
            action = action_by_ref[ref]
            if ref in unresolved:
                cycle_deps = tuple(sorted(
                    (dependency for dependency in dependencies[ref] if dependency in unresolved),
                    key=lambda dependency: (
                        dependency.entity_type,
                        dependency.entity_id,
                        dependency.version,
                    ),
                ))
                result.append(
                    PlannedAction(
                        artifact_ref=ref,
                        action_type=ActionType.ESCALATE,
                        status=ActionStatus.BLOCKED,
                        priority=_BLOCKED_PRIORITY,
                        reason=(
                            "Dependency cycle detected: "
                            + ",".join(
                                f"{item.entity_type}:{item.entity_id}@{item.version}"
                                for item in (ref, *cycle_deps)
                            )
                        ),
                        requires_human_authority=True,
                        blocked_by=cycle_deps,
                    )
                )
            else:
                result.append(
                    PlannedAction(
                        artifact_ref=action.artifact_ref,
                        action_type=action.action_type,
                        status=action.status,
                        priority=priority,
                        reason=action.reason,
                        requires_human_authority=action.requires_human_authority,
                        blocked_by=action.blocked_by,
                    )
                )
        return result

    @staticmethod
    def _is_malformed_discrepancy(discrepancy: dict[str, Any]) -> bool:
        reference = discrepancy.get("reference")
        return not isinstance(reference, dict) or not _REFERENCE_KEYS.issubset(reference)


__all__ = [
    "ActionType",
    "ActionStatus",
    "PlannedAction",
    "ReactionPlan",
    "ReactionPlanner",
]
