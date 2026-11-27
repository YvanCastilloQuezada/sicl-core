import json
from pathlib import Path

FIXTURE = Path(__file__).parent / "fixtures" / "resolver_redteam_r03.json"

EXPECTED_IDS = [f"RT-R{i:02d}" for i in range(1, 29)]
VALID_EXPECTATIONS = {
    "REUSE_ID",
    "NO_REUSE",
    "SAME_IDENTITY",
    "SAME_CANONICAL_IDENTITY",
    "CONFLICT",
    "REVIEW_REQUIRED",
    "DECOMPOSITION_REQUIRED",
    "REJECTED",
    "INVALID_RECORD",
    "FAIL_CLOSED",
    "DETERMINISTIC",
}

EXPECTED_LEVELS = [
    "L1_domain",
    "L2_family",
    "L3_intent",
    "L4_operation",
    "L5_entity",
    "L6_type",
    "L7_mode",
    "L8_output",
]


def load_vectors():
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def test_r03_fixture_exists_and_is_valid_json():
    assert FIXTURE.is_file()
    data = load_vectors()
    assert data["contract"] == "ARKI-UCG-RESOLVER-R03"
    assert data["version"] == "1.0.0"


def test_identity_levels_are_exactly_eight_and_ordered():
    data = load_vectors()
    assert data["identity_levels"] == EXPECTED_LEVELS
    assert len(data["identity_levels"]) == 8


def test_red_team_matrix_has_28_unique_cases():
    cases = load_vectors()["cases"]
    ids = [case["id"] for case in cases]
    assert ids == EXPECTED_IDS
    assert len(ids) == len(set(ids)) == 28


def test_each_case_has_scenario_and_expectation():
    for case in load_vectors()["cases"]:
        assert case["scenario"]
        assert case["expected"] in VALID_EXPECTATIONS


def test_reuse_is_only_expected_for_exact_or_normalization_variations():
    cases = load_vectors()["cases"]
    reuse_cases = [
        case["id"] for case in cases
        if case["expected"] == "REUSE_ID"
    ]
    assert reuse_cases == ["RT-R01", "RT-R02", "RT-R03"]


def test_missing_identity_level_is_rejected():
    cases = load_vectors()["cases"]
    case = next(c for c in cases if c["id"] == "RT-R18")
    assert case["expected"] == "REJECTED"


def test_registry_integrity_cases_fail_closed():
    cases = load_vectors()["cases"]
    expectations = {c["id"]: c["expected"] for c in cases}
    assert expectations["RT-R15"] == "CONFLICT"
    assert expectations["RT-R23"] == "INVALID_RECORD"
    assert expectations["RT-R24"] == "FAIL_CLOSED"


def test_similarity_never_authorizes_reuse():
    cases = load_vectors()["cases"]
    expectations = {c["id"]: c["expected"] for c in cases}
    assert expectations["RT-R26"] == "NO_REUSE"
    assert expectations["RT-R16"] == "REVIEW_REQUIRED"


def test_normalization_collision_is_policy_defined_equivalence():
    cases = load_vectors()
    case = next(c for c in cases["cases"] if c["id"] == "RT-R22")
    assert case["expected"] == "SAME_CANONICAL_IDENTITY"


def test_composite_intent_requires_decomposition():
    cases = load_vectors()["cases"]
    case = next(c for c in cases if c["id"] == "RT-R17")
    assert case["expected"] == "DECOMPOSITION_REQUIRED"
