from __future__ import annotations

import re
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


_CAMEL_CONFIG = ConfigDict(extra="forbid", populate_by_name=True)
_SHA256_HEX = re.compile(r"^[0-9a-f]{64}$")


def _is_sha256_hex(value: str) -> bool:
    return bool(_SHA256_HEX.fullmatch(value))


class DeveloperProvenanceRefSchema(BaseModel):
    model_config = _CAMEL_CONFIG

    source: str = Field(min_length=1)
    ref: str = Field(min_length=1)
    fingerprint: str | None = None

    @model_validator(mode="after")
    def _validate_fingerprint(self):
        if self.fingerprint is not None and not _is_sha256_hex(self.fingerprint):
            raise ValueError("fingerprint must be lowercase sha256 hex")
        return self


class DeveloperUnknownSchema(BaseModel):
    model_config = _CAMEL_CONFIG

    field: str = Field(min_length=1)
    reason: str = Field(min_length=1)
    required_evidence: str = Field(alias="requiredEvidence", min_length=1)


class DeveloperHumanActionSchema(BaseModel):
    model_config = _CAMEL_CONFIG

    action: str = Field(min_length=1)
    reason: str = Field(min_length=1)


class DeveloperMutationSchema(BaseModel):
    model_config = _CAMEL_CONFIG

    kind: str = Field(min_length=1)
    target_provisional_id: str = Field(alias="targetProvisionalId", min_length=1)
    before: dict[str, Any]
    after: dict[str, Any]


class DeveloperFeedbackLoopSchema(BaseModel):
    model_config = _CAMEL_CONFIG

    from_: str = Field(alias="from", min_length=1)
    to: str = Field(min_length=1)
    reason: str = Field(min_length=1)


class ProposedArchiElementDTOSchema(BaseModel):
    model_config = _CAMEL_CONFIG

    provisional_id: str = Field(alias="provisionalId", min_length=1)
    kind: str = Field(min_length=1)
    geometry: dict[str, Any] | None
    properties: dict[str, Any]
    provenance: list[DeveloperProvenanceRefSchema]
    epistemic_status: Literal["FACT", "ASSUMPTION", "HYPOTHESIS", "UNKNOWN"] = Field(alias="epistemicStatus")

    @model_validator(mode="after")
    def _validate_element(self):
        if self.epistemic_status == "UNKNOWN":
            raise ValueError("element epistemicStatus must not be UNKNOWN; use unresolvedUnknowns")
        if self.properties.get("canonical") is True:
            raise ValueError("element cannot declare properties.canonical=true")
        return self


class ProposedArchiRelationDTOSchema(BaseModel):
    model_config = _CAMEL_CONFIG

    from_provisional_id: str = Field(alias="fromProvisionalId", min_length=1)
    to_provisional_id: str = Field(alias="toProvisionalId", min_length=1)
    relation_kind: str = Field(alias="relationKind", min_length=1)
    provenance: list[DeveloperProvenanceRefSchema]


class ProposedDerivationDTOSchema(BaseModel):
    model_config = _CAMEL_CONFIG

    output_provisional_id: str = Field(alias="outputProvisionalId", min_length=1)
    inputs_provisional_ids: list[str] = Field(alias="inputsProvisionalIds")
    method: str = Field(min_length=1)
    method_version: str = Field(alias="methodVersion", min_length=1)
    assumptions: list[str]


class DeveloperProposalSchema(BaseModel):
    model_config = _CAMEL_CONFIG

    proposal_id: str = Field(alias="proposalId", min_length=1)
    parent_proposal_id: str | None = Field(alias="parentProposalId")
    source_execution_id: str = Field(alias="sourceExecutionId", min_length=1)
    source_d63: str = Field(alias="sourceD63", min_length=1)
    fingerprint: str
    epistemic_status: Literal["HYPOTHESIS", "PROPOSAL"] = Field(alias="epistemicStatus")
    proposed_elements: list[ProposedArchiElementDTOSchema] = Field(alias="proposedElements")
    proposed_relations: list[ProposedArchiRelationDTOSchema] = Field(alias="proposedRelations")
    proposed_derivations: list[ProposedDerivationDTOSchema] = Field(alias="proposedDerivations")
    unresolved_unknowns: list[DeveloperUnknownSchema] = Field(alias="unresolvedUnknowns")
    required_human_actions: list[DeveloperHumanActionSchema] = Field(alias="requiredHumanActions")
    provenance: list[DeveloperProvenanceRefSchema]
    review_required: Literal[True] = Field(alias="reviewRequired")
    mutation: DeveloperMutationSchema | None
    rejected_because: str | None = Field(alias="rejectedBecause")
    feedback_loops: list[DeveloperFeedbackLoopSchema] = Field(alias="feedbackLoops")

    @model_validator(mode="after")
    def _validate_invariants(self):
        if not _is_sha256_hex(self.fingerprint):
            raise ValueError("fingerprint must be lowercase sha256 hex")
        if self.parent_proposal_id is not None and self.parent_proposal_id == self.proposal_id:
            raise ValueError("parentProposalId must differ from proposalId")

        element_ids = [element.provisional_id for element in self.proposed_elements]
        if len(set(element_ids)) != len(element_ids):
            raise ValueError("provisionalId must be unique")
        declared = set(element_ids)

        for relation in self.proposed_relations:
            if relation.from_provisional_id not in declared:
                raise ValueError(f"fromProvisionalId {relation.from_provisional_id} not declared")
            if relation.to_provisional_id not in declared:
                raise ValueError(f"toProvisionalId {relation.to_provisional_id} not declared")

        for derivation in self.proposed_derivations:
            if derivation.output_provisional_id not in declared:
                raise ValueError(f"outputProvisionalId {derivation.output_provisional_id} not declared")
            for input_id in derivation.inputs_provisional_ids:
                if input_id not in declared:
                    raise ValueError(f"inputProvisionalId {input_id} not declared")
        return self
