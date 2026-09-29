import copy

import pytest
from pydantic import ValidationError

from api.schemas_developer import DeveloperProposalSchema


def valid_proposal():
    return {
        "proposalId": "dev-prop-001",
        "parentProposalId": None,
        "sourceExecutionId": "exec-d63-001",
        "sourceD63": "d63-result-abc",
        "fingerprint": "a" * 64,
        "epistemicStatus": "HYPOTHESIS",
        "proposedElements": [
            {
                "provisionalId": "el-a",
                "kind": "SPACE",
                "geometry": {"x": 0},
                "properties": {},
                "provenance": [{"source": "d63", "ref": "a"}],
                "epistemicStatus": "HYPOTHESIS",
            },
            {
                "provisionalId": "el-b",
                "kind": "SPACE",
                "geometry": None,
                "properties": {},
                "provenance": [{"source": "d63", "ref": "b"}],
                "epistemicStatus": "FACT",
            },
        ],
        "proposedRelations": [
            {
                "fromProvisionalId": "el-a",
                "toProvisionalId": "el-b",
                "relationKind": "ADJACENT_TO",
                "provenance": [{"source": "parti", "ref": "r1"}],
            }
        ],
        "proposedDerivations": [
            {
                "outputProvisionalId": "el-b",
                "inputsProvisionalIds": ["el-a"],
                "method": "derive",
                "methodVersion": "1",
                "assumptions": [],
            }
        ],
        "unresolvedUnknowns": [
            {"field": "opening", "reason": "unknown", "requiredEvidence": "human decision"}
        ],
        "requiredHumanActions": [{"action": "review", "reason": "pre-D-2"}],
        "provenance": [{"source": "d63", "ref": "d63-result-abc"}],
        "reviewRequired": True,
        "mutation": None,
        "rejectedBecause": None,
        "feedbackLoops": [{"from": "developer", "to": "d63", "reason": "feedback"}],
    }


def invalid(data):
    with pytest.raises(ValidationError):
        DeveloperProposalSchema.model_validate(data)


def test_accepts_valid_camel_case_proposal():
    model = DeveloperProposalSchema.model_validate(valid_proposal())
    assert model.proposal_id == "dev-prop-001"
    assert model.source_d63 == "d63-result-abc"


def test_accepts_snake_case_by_field_name():
    model = DeveloperProposalSchema.model_validate(valid_proposal())
    snake = model.model_dump()
    assert DeveloperProposalSchema.model_validate(snake) == model


def test_dump_by_alias_uses_wire_contract():
    dumped = DeveloperProposalSchema.model_validate(valid_proposal()).model_dump(by_alias=True)
    assert dumped["proposalId"] == "dev-prop-001"
    assert dumped["sourceD63"] == "d63-result-abc"
    assert dumped["feedbackLoops"][0]["from"] == "developer"
    assert "proposal_id" not in dumped


@pytest.mark.parametrize("fingerprint", ["A" * 64, "a" * 63, "g" * 64])
def test_rejects_invalid_proposal_fingerprint(fingerprint):
    data = valid_proposal()
    data["fingerprint"] = fingerprint
    invalid(data)


@pytest.mark.parametrize("field", ["proposalId", "sourceExecutionId", "sourceD63"])
def test_rejects_empty_required_identity(field):
    data = valid_proposal()
    data[field] = ""
    invalid(data)


def test_rejects_parent_equal_to_proposal():
    data = valid_proposal()
    data["parentProposalId"] = data["proposalId"]
    invalid(data)


def test_rejects_invalid_proposal_epistemic_status():
    data = valid_proposal()
    data["epistemicStatus"] = "FACT"
    invalid(data)


def test_rejects_review_required_false():
    data = valid_proposal()
    data["reviewRequired"] = False
    invalid(data)


def test_rejects_extra_proposal_field():
    data = valid_proposal()
    data["unexpected"] = True
    invalid(data)


def test_rejects_duplicate_provisional_id():
    data = valid_proposal()
    data["proposedElements"][1]["provisionalId"] = "el-a"
    invalid(data)


def test_rejects_empty_provisional_id():
    data = valid_proposal()
    data["proposedElements"][0]["provisionalId"] = ""
    invalid(data)


def test_rejects_unknown_element():
    data = valid_proposal()
    data["proposedElements"][0]["epistemicStatus"] = "UNKNOWN"
    invalid(data)


def test_rejects_element_claiming_canonical():
    data = valid_proposal()
    data["proposedElements"][0]["properties"]["canonical"] = True
    invalid(data)


@pytest.mark.parametrize("key,value", [("source", ""), ("fingerprint", "BAD")])
def test_rejects_invalid_element_provenance(key, value):
    data = valid_proposal()
    data["proposedElements"][0]["provenance"][0][key] = value
    invalid(data)


@pytest.mark.parametrize("endpoint", ["fromProvisionalId", "toProvisionalId"])
def test_rejects_relation_to_undeclared_element(endpoint):
    data = valid_proposal()
    data["proposedRelations"][0][endpoint] = "missing"
    invalid(data)


def test_rejects_invalid_relation_provenance():
    data = valid_proposal()
    data["proposedRelations"][0]["provenance"][0]["ref"] = ""
    invalid(data)


def test_rejects_derivation_output_not_declared():
    data = valid_proposal()
    data["proposedDerivations"][0]["outputProvisionalId"] = "missing"
    invalid(data)


def test_rejects_derivation_input_not_declared():
    data = valid_proposal()
    data["proposedDerivations"][0]["inputsProvisionalIds"] = ["missing"]
    invalid(data)


def test_rejects_unknown_with_empty_field():
    data = valid_proposal()
    data["unresolvedUnknowns"][0]["field"] = ""
    invalid(data)


def test_required_evidence_alias_maps_to_snake_case():
    model = DeveloperProposalSchema.model_validate(valid_proposal())
    assert model.unresolved_unknowns[0].required_evidence == "human decision"


@pytest.mark.parametrize("key,value", [("source", ""), ("fingerprint", "NOT_HEX")])
def test_rejects_invalid_global_provenance(key, value):
    data = valid_proposal()
    data["provenance"][0][key] = value
    invalid(data)


def test_feedback_from_alias_maps_to_from_field():
    model = DeveloperProposalSchema.model_validate(valid_proposal())
    assert model.feedback_loops[0].from_ == "developer"


def test_rejects_extra_nested_field():
    data = valid_proposal()
    data["proposedElements"][0]["unexpected"] = True
    invalid(data)


def test_round_trip_by_alias_is_idempotent():
    first = DeveloperProposalSchema.model_validate(valid_proposal())
    second = DeveloperProposalSchema.model_validate(first.model_dump(by_alias=True))
    assert second == first


def test_accepts_valid_nested_provenance_fingerprint():
    data = valid_proposal()
    data["proposedElements"][0]["provenance"][0]["fingerprint"] = "b" * 64
    assert DeveloperProposalSchema.model_validate(data)


def test_does_not_mutate_input_payload():
    data = valid_proposal()
    before = copy.deepcopy(data)
    DeveloperProposalSchema.model_validate(data)
    assert data == before
