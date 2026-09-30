"""Drawing faculty: advisor and independent examiner for DAM graduation.

The advisor interprets evidence. The examiner grades immutable observations.
Neither mutates D2, drawing output, or graduation state.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .model import DamError, GraduationLevel


class ExamOutcome(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    INSUFFICIENT_DATA = "INSUFFICIENT_DATA"


@dataclass(frozen=True)
class DrawingObservation:
    case_id: str
    source_fingerprint: str
    vector_output: bool
    deterministic_output: bool
    source_traceability: bool
    projection_before_style: bool
    cut_visibility_resolved: bool
    annotation_separated: bool
    fail_closed_on_unsupported: bool
    external_runtime_dependencies: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.case_id.strip():
            raise DamError("case_id is required")
        if len(self.source_fingerprint) != 64:
            raise DamError("source_fingerprint must be SHA-256")


@dataclass(frozen=True)
class AdvisorAssessment:
    branch_id: str
    observations: tuple[str, ...]
    missing_evidence: tuple[str, ...]
    recommended_level: GraduationLevel


class DrawingAdvisor:
    advisor_id = "DRAWING_ADVISOR_V1"

    def assess(self, observation: DrawingObservation) -> AdvisorAssessment:
        missing = []
        if not observation.source_traceability:
            missing.append("SOURCE_TRACEABILITY")
        if not observation.deterministic_output:
            missing.append("DETERMINISM")
        if observation.external_runtime_dependencies:
            missing.append("RUNTIME_INDEPENDENCE")
        level = GraduationLevel.REPRODUCTION
        if not missing and observation.vector_output and observation.projection_before_style:
            level = GraduationLevel.GENERALIZATION
        return AdvisorAssessment("DRAWING", (), tuple(missing), level)


@dataclass(frozen=True)
class ExamCase:
    exam_id: str
    minimum_level: GraduationLevel
    blind: bool = True
    adversarial: bool = False


@dataclass(frozen=True)
class ExamResult:
    exam_id: str
    outcome: ExamOutcome
    failed_checks: tuple[str, ...]
    awarded_level: GraduationLevel


class DrawingExaminer:
    examiner_id = "DRAWING_EXAMINER_V1"

    def grade(self, case: ExamCase, observation: DrawingObservation) -> ExamResult:
        checks = {
            "VECTOR_OUTPUT": observation.vector_output,
            "DETERMINISM": observation.deterministic_output,
            "TRACEABILITY": observation.source_traceability,
            "PROJECTION_BEFORE_STYLE": observation.projection_before_style,
            "CUT_VISIBILITY": observation.cut_visibility_resolved,
            "ANNOTATION_SEPARATION": observation.annotation_separated,
            "FAIL_CLOSED": observation.fail_closed_on_unsupported,
            "RUNTIME_INDEPENDENCE": not observation.external_runtime_dependencies,
        }
        failed = tuple(name for name, passed in checks.items() if not passed)
        if failed:
            return ExamResult(case.exam_id, ExamOutcome.FAIL, failed, GraduationLevel.UNKNOWN)
        if case.minimum_level >= GraduationLevel.COMPARATIVE and not case.blind:
            return ExamResult(case.exam_id, ExamOutcome.INSUFFICIENT_DATA, ("BLIND_CASE_REQUIRED",), GraduationLevel.UNKNOWN)
        if case.minimum_level >= GraduationLevel.ADVERSARIAL and not case.adversarial:
            return ExamResult(case.exam_id, ExamOutcome.INSUFFICIENT_DATA, ("ADVERSARIAL_CASE_REQUIRED",), GraduationLevel.UNKNOWN)
        return ExamResult(case.exam_id, ExamOutcome.PASS, (), case.minimum_level)


DRAWING_EXAM_BANK = (
    ExamCase("DRAW-L3-REPRODUCTION", GraduationLevel.REPRODUCTION, blind=False),
    ExamCase("DRAW-L4-GENERALIZATION", GraduationLevel.GENERALIZATION),
    ExamCase("DRAW-L5-ADVERSARIAL", GraduationLevel.ADVERSARIAL, adversarial=True),
    ExamCase("DRAW-L6-COMPARATIVE-BLIND", GraduationLevel.COMPARATIVE, adversarial=True),
    ExamCase("DRAW-L7-INDEPENDENCE", GraduationLevel.RUNTIME_INDEPENDENCE, adversarial=True),
)
