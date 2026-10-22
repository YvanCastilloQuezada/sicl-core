"""DAM learning constitution: master -> knowledge -> DNA -> advisor -> examiner.

External masters are evidence producers in learning only.  This module contains
no adapter to, import of, or runtime dependency on an external master.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class DamError(ValueError):
    pass


class LearningRole(str, Enum):
    MASTER = "MASTER"
    ADVISOR = "ADVISOR"
    EXAMINER = "EXAMINER"
    NATIVE_ENGINE = "NATIVE_ENGINE"


class GraduationLevel(int, Enum):
    UNKNOWN = 0
    OBSERVATION = 1
    COMPREHENSION = 2
    REPRODUCTION = 3
    GENERALIZATION = 4
    ADVERSARIAL = 5
    COMPARATIVE = 6
    RUNTIME_INDEPENDENCE = 7
    ARCHITECTURAL_INTEGRATION = 8
    PROFESSIONAL_EXAM = 9
    GRADUATED_DNA = 10


@dataclass(frozen=True)
class EvidenceRef:
    evidence_id: str
    source: str
    fingerprint: str

    def __post_init__(self) -> None:
        if not self.evidence_id.strip() or not self.source.strip():
            raise DamError("evidence_id and source are required")
        if len(self.fingerprint) != 64 or any(c not in "0123456789abcdef" for c in self.fingerprint):
            raise DamError("fingerprint must be a lowercase SHA-256 digest")


@dataclass(frozen=True)
class KnowledgeRule:
    rule_id: str
    statement: str
    evidence: tuple[EvidenceRef, ...]
    scope: str
    confidence: float

    def __post_init__(self) -> None:
        if not self.rule_id.strip() or not self.statement.strip() or not self.scope.strip():
            raise DamError("rule_id, statement and scope are required")
        if not self.evidence:
            raise DamError("KNOWLEDGE_WITHOUT_SOURCE")
        if not 0.0 <= self.confidence <= 1.0:
            raise DamError("confidence must be between 0 and 1")


@dataclass(frozen=True)
class BranchFaculty:
    branch_id: str
    advisor_id: str
    examiner_id: str
    native_engine_id: str

    def __post_init__(self) -> None:
        identities = (self.advisor_id, self.examiner_id, self.native_engine_id)
        if not self.branch_id.strip() or any(not item.strip() for item in identities):
            raise DamError("branch and faculty identities are required")
        if len(set(identities)) != len(identities):
            raise DamError("MASTER/ADVISOR/EXAMINER/NATIVE_ENGINE roles must remain separated")


@dataclass(frozen=True)
class GraduationRecord:
    branch_id: str
    level: GraduationLevel
    passed_exam_ids: tuple[str, ...] = ()
    master_runtime_dependencies: tuple[str, ...] = ()
    human_review_id: str | None = None

    def __post_init__(self) -> None:
        if self.level is GraduationLevel.GRADUATED_DNA:
            if self.master_runtime_dependencies:
                raise DamError("EXTERNAL_ENGINE_RUNTIME_DEPENDENCY")
            if not self.human_review_id:
                raise DamError("HUMAN_REVIEW_REQUIRED")
            if not self.passed_exam_ids:
                raise DamError("EXAM_EVIDENCE_REQUIRED")

    @property
    def production_eligible(self) -> bool:
        return self.level is GraduationLevel.GRADUATED_DNA and not self.master_runtime_dependencies


def assert_role_separation(master_ids: tuple[str, ...], faculty: BranchFaculty) -> None:
    reserved = {faculty.advisor_id, faculty.examiner_id, faculty.native_engine_id}
    overlap = reserved.intersection(master_ids)
    if overlap:
        raise DamError(f"ROLE_COLLISION: {','.join(sorted(overlap))}")
