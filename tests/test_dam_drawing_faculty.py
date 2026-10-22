from sicl.dam.drawing_faculty import (
    DRAWING_EXAM_BANK, DrawingAdvisor, DrawingExaminer, DrawingObservation,
    ExamCase, ExamOutcome,
)
from sicl.dam import GraduationLevel


HASH = "a" * 64


def observation(**changes):
    values = dict(
        case_id="DRAW-CASE-001", source_fingerprint=HASH, vector_output=True,
        deterministic_output=True, source_traceability=True,
        projection_before_style=True, cut_visibility_resolved=True,
        annotation_separated=True, fail_closed_on_unsupported=True,
        external_runtime_dependencies=(),
    )
    values.update(changes)
    return DrawingObservation(**values)


def test_drawing_faculty_has_separate_identities():
    assert DrawingAdvisor.advisor_id != DrawingExaminer.examiner_id


def test_advisor_reports_missing_evidence_without_graduating():
    result = DrawingAdvisor().assess(observation(source_traceability=False))
    assert "SOURCE_TRACEABILITY" in result.missing_evidence
    assert result.recommended_level < GraduationLevel.GRADUATED_DNA


def test_examiner_passes_complete_reproduction_evidence():
    case = ExamCase("E", GraduationLevel.REPRODUCTION, blind=False)
    result = DrawingExaminer().grade(case, observation())
    assert result.outcome is ExamOutcome.PASS
    assert result.awarded_level is GraduationLevel.REPRODUCTION


def test_examiner_fails_runtime_master_dependency():
    case = ExamCase("E", GraduationLevel.RUNTIME_INDEPENDENCE, adversarial=True)
    result = DrawingExaminer().grade(case, observation(external_runtime_dependencies=("ifcopenshell.draw",)))
    assert result.outcome is ExamOutcome.FAIL
    assert "RUNTIME_INDEPENDENCE" in result.failed_checks


def test_examiner_fails_silent_unsupported_behavior():
    case = ExamCase("E", GraduationLevel.ADVERSARIAL, adversarial=True)
    result = DrawingExaminer().grade(case, observation(fail_closed_on_unsupported=False))
    assert result.outcome is ExamOutcome.FAIL
    assert "FAIL_CLOSED" in result.failed_checks


def test_comparative_exam_must_be_blind():
    case = ExamCase("E", GraduationLevel.COMPARATIVE, blind=False, adversarial=True)
    result = DrawingExaminer().grade(case, observation())
    assert result.outcome is ExamOutcome.INSUFFICIENT_DATA
    assert result.failed_checks == ("BLIND_CASE_REQUIRED",)


def test_adversarial_exam_cannot_be_relabelled_from_normal_fixture():
    case = ExamCase("E", GraduationLevel.ADVERSARIAL, adversarial=False)
    result = DrawingExaminer().grade(case, observation())
    assert result.outcome is ExamOutcome.INSUFFICIENT_DATA
    assert result.failed_checks == ("ADVERSARIAL_CASE_REQUIRED",)


def test_exam_bank_covers_reproduction_through_runtime_independence():
    assert tuple(case.minimum_level for case in DRAWING_EXAM_BANK) == (
        GraduationLevel.REPRODUCTION,
        GraduationLevel.GENERALIZATION,
        GraduationLevel.ADVERSARIAL,
        GraduationLevel.COMPARATIVE,
        GraduationLevel.RUNTIME_INDEPENDENCE,
    )
