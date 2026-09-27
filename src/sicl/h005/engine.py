"""H-005 selective recomputation engine.

This module is the first executor downstream of H-004. It never modifies H-001
through H-004 and only persists a handler-produced DerivationRecord through the
official DerivationLedger.record interface.
"""
from __future__ import annotations

from dataclasses import replace
from typing import Mapping

from ..derivation import DerivationLedger, DerivationRecord, VersionedRef
from ..reaction import ActionStatus, ActionType, PlannedAction, ReactionPlan
from .contract import (
    ExecutionRecord,
    ExecutionStatus,
    H005ExecutionReport,
    RecomputationCandidate,
)
from .registry import AmbiguousHandlerError, HandlerNotRegisteredError, RecomputationRegistry


class SelectiveRecomputationEngine:
    def __init__(self, ledger: DerivationLedger, registry: RecomputationRegistry) -> None:
        self.ledger = ledger
        self.registry = registry

    def execute(
        self,
        project_id: str,
        reaction_plan: ReactionPlan,
        current_refs: Mapping[tuple[str, str], VersionedRef],
    ) -> H005ExecutionReport:
        if not isinstance(project_id, str) or not project_id.strip():
            raise ValueError("project_id must be non-empty")
        if not isinstance(reaction_plan, ReactionPlan) or reaction_plan.read_only is not True:
            raise ValueError("reaction_plan must be a read-only ReactionPlan")
        if not isinstance(current_refs, Mapping):
            raise ValueError("current_refs must be a mapping")

        records: list[ExecutionRecord] = []
        effective_refs = dict(current_refs)
        for action in reaction_plan.planned_actions:
            result = self._execute_action(project_id, reaction_plan, action, effective_refs)
            records.append(result)
            if result.status is ExecutionStatus.EXECUTED and result.new_output is not None:
                effective_refs[result.new_output.key()] = result.new_output
        return H005ExecutionReport(tuple(records), read_only=False)

    def _execute_action(
        self,
        project_id: str,
        plan: ReactionPlan,
        action: PlannedAction,
        current_refs: Mapping[tuple[str, str], VersionedRef],
    ) -> ExecutionRecord:
        empty_inputs: tuple[VersionedRef, ...] = ()
        if not isinstance(action, PlannedAction):
            return self._blocked(project_id, action, "MALFORMED_PLAN", empty_inputs)
        try:
            candidate = RecomputationCandidate.from_action(action, method="placeholder", method_version="placeholder")
        except Exception as exc:
            return self._rejected(project_id, action, f"ACTION_NOT_ELIGIBLE:{exc}", empty_inputs)

        artifact_validity = next(
            (item for item in plan.validity_report.artifact_validities if item.artifact_ref.key() == action.artifact_ref.key()),
            None,
        )
        if artifact_validity is None:
            return self._blocked(project_id, action, "MALFORMED_PLAN", empty_inputs)
        if artifact_validity.state != "FULLY_STALE":
            return self._blocked(project_id, action, "STALE_OR_INVALID_PLAN", empty_inputs)

        project_records = self.ledger.list(project_id)
        matching = [
            item for item in project_records
            if item.output.key() == action.artifact_ref.key() and item.output.version == action.artifact_ref.version
        ]
        if not matching:
            return self._blocked(project_id, action, "DERIVATION_NOT_FOUND", empty_inputs)
        if len(matching) != 1:
            return self._blocked(project_id, action, "AMBIGUOUS_DERIVATION", tuple(matching[0].inputs))
        previous = matching[0]
        if any(item.output.key() == previous.output.key() and item.output.version > previous.output.version for item in project_records):
            return self._blocked(project_id, action, "STALE_PLAN", previous.inputs)

        try:
            handler = self.registry.resolve(previous.method, previous.method_version)
        except HandlerNotRegisteredError:
            return self._blocked(project_id, action, "HANDLER_NOT_REGISTERED", previous.inputs, previous)
        except AmbiguousHandlerError:
            return self._blocked(project_id, action, "AMBIGUOUS_HANDLER", previous.inputs, previous)

        try:
            produced = handler(project_id, previous, current_refs)
        except Exception as exc:
            return self._blocked(project_id, action, f"HANDLER_EXCEPTION:{type(exc).__name__}", previous.inputs, previous)
        validation_error = self._validate_output(previous, produced, current_refs, project_records)
        if validation_error is not None:
            return self._blocked(project_id, action, validation_error, previous.inputs, previous)

        self.ledger.record(project_id, produced, actor="H005_SELECTIVE_RECOMPUTATION")
        return ExecutionRecord(
            project_id=project_id,
            artifact_requested=action.artifact_ref,
            derivation_selected=previous.id,
            method=produced.method,
            method_version=produced.method_version,
            inputs=produced.inputs,
            previous_output=previous.output,
            new_output=produced.output,
            status=ExecutionStatus.EXECUTED,
            reason="RECOMPUTATION_EXECUTED",
        )

    @staticmethod
    def _validate_output(
        previous: DerivationRecord,
        produced: object,
        current_refs: Mapping[tuple[str, str], VersionedRef],
        existing: list[DerivationRecord],
    ) -> str | None:
        if not isinstance(produced, DerivationRecord):
            return "MALFORMED_HANDLER_OUTPUT"
        if any(item.id == produced.id for item in existing):
            return "DUPLICATE_EXECUTION"
        if produced.output.key() != previous.output.key() or produced.output.version <= previous.output.version:
            return "INVALID_OUTPUT_IDENTITY_OR_VERSION"
        if produced.method != previous.method or produced.method_version != previous.method_version:
            return "PROVENANCE_METHOD_MISMATCH"
        if produced.assumptions != previous.assumptions or produced.project_context_version != previous.project_context_version:
            return "PROVENANCE_CONTEXT_MISMATCH"
        old_keys = {(item.entity_type, item.entity_id) for item in previous.inputs}
        new_keys = {(item.entity_type, item.entity_id) for item in produced.inputs}
        if old_keys != new_keys:
            return "PROVENANCE_INPUT_SET_MISMATCH"
        for item in produced.inputs:
            current = current_refs.get(item.key())
            if current is not None and item != current:
                return "INPUT_REF_NOT_CURRENT"
        relation_keys = {(relation.to_ref.entity_type, relation.to_ref.entity_id, relation.to_ref.version) for relation in produced.relations if relation.from_ref == produced.output}
        expected_keys = {(item.entity_type, item.entity_id, item.version) for item in produced.inputs}
        if relation_keys != expected_keys:
            return "PROVENANCE_RELATIONS_MISMATCH"
        return None

    @staticmethod
    def _blocked(project_id: str, action: PlannedAction, reason: str, inputs: tuple[VersionedRef, ...], previous: DerivationRecord | None = None) -> ExecutionRecord:
        return ExecutionRecord(project_id, action.artifact_ref, previous.id if previous else None, previous.method if previous else None, previous.method_version if previous else None, inputs, previous.output if previous else None, None, ExecutionStatus.BLOCKED, reason)

    @staticmethod
    def _rejected(project_id: str, action: PlannedAction, reason: str, inputs: tuple[VersionedRef, ...]) -> ExecutionRecord:
        return ExecutionRecord(project_id, action.artifact_ref, None, None, None, inputs, None, None, ExecutionStatus.REJECTED, reason)


__all__ = ["SelectiveRecomputationEngine"]
