from __future__ import annotations

import pytest

from sicl.dam import (
    BranchFaculty, DamError, EvidenceRef, GraduationLevel, GraduationRecord,
    KnowledgeRule, LearningRole, assert_role_separation,
)


HASH = "a" * 64


def test_constitutional_roles_are_explicit_and_distinct():
    assert {role.value for role in LearningRole} == {"MASTER", "ADVISOR", "EXAMINER", "NATIVE_ENGINE"}
    faculty = BranchFaculty("DRAWING", "DRAWING_ADVISOR", "DRAWING_EXAMINER", "ARKI_DRAW_NATIVE")
    assert_role_separation(("IFCOPENSHELL_DRAW", "FREECAD_TECHDRAW"), faculty)


def test_faculty_cannot_collapse_advisor_examiner_and_native_engine():
    with pytest.raises(DamError, match="roles must remain separated"):
        BranchFaculty("DRAWING", "SAME", "SAME", "ARKI_DRAW_NATIVE")


def test_external_master_cannot_impersonate_faculty_role():
    faculty = BranchFaculty("DRAWING", "DRAWING_ADVISOR", "DRAWING_EXAMINER", "ARKI_DRAW_NATIVE")
    with pytest.raises(DamError, match="ROLE_COLLISION"):
        assert_role_separation(("IFCOPENSHELL_DRAW", "DRAWING_EXAMINER"), faculty)


def test_knowledge_without_source_is_forbidden():
    with pytest.raises(DamError, match="KNOWLEDGE_WITHOUT_SOURCE"):
        KnowledgeRule("R1", "Project geometry before styling", (), "DRAWING", 0.8)


def test_sourced_knowledge_can_enter_learning_record():
    evidence = EvidenceRef("GT-001", "IfcOpenShell Draw 0.8.5 fixture", HASH)
    rule = KnowledgeRule("R1", "Resolve projection before styling", (evidence,), "DRAWING", 0.8)
    assert rule.evidence == (evidence,)


def test_graduated_dna_rejects_external_runtime_dependency():
    with pytest.raises(DamError, match="EXTERNAL_ENGINE_RUNTIME_DEPENDENCY"):
        GraduationRecord(
            "DRAWING", GraduationLevel.GRADUATED_DNA, ("EXAM-10",),
            ("ifcopenshell.draw",), "HUMAN-REVIEW-1",
        )


def test_graduated_dna_requires_exam_and_human_review():
    with pytest.raises(DamError, match="HUMAN_REVIEW_REQUIRED"):
        GraduationRecord("DRAWING", GraduationLevel.GRADUATED_DNA, ("EXAM-10",))
    with pytest.raises(DamError, match="EXAM_EVIDENCE_REQUIRED"):
        GraduationRecord("DRAWING", GraduationLevel.GRADUATED_DNA, (), (), "HUMAN-REVIEW-1")


def test_only_level_10_is_production_eligible():
    for level in GraduationLevel:
        record = GraduationRecord("DRAWING", level)
        if level is GraduationLevel.GRADUATED_DNA:
            record = GraduationRecord("DRAWING", level, ("EXAM-10",), (), "HUMAN-REVIEW-1")
        assert record.production_eligible is (level is GraduationLevel.GRADUATED_DNA)
