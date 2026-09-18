from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


EPISTEMIC_STATES = {
    "SOURCE_DERIVED",
    "SIMS_DEI_DERIVED_INTERPRETATION",
    "HUMAN_STATED",
    "PROJECT_OBSERVED",
    "COMPUTATIONALLY_OBSERVED",
    "UNKNOWN",
    "REQUIRES_EVIDENCE",
}


@dataclass(frozen=True)
class ArchitecturalForce:
    force_id: str
    origin_type: str
    description: str
    spatial_scope: str
    epistemic_status: str
    evidence_state: str
    applicability: str = "CONTEXTUAL"
    limitations: str = "Interpretation; not an objective, constraint or requirement."
    provenance: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ArchitecturalTension:
    tension_id: str
    force_ids: list[str]
    why_it_may_exist: str
    context: str
    spatial_scope: str
    derivation: str
    epistemic_status: str
    provenance: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class SpatialRelationship:
    relationship_id: str
    relationship_type: str
    subject: str
    object: str
    spatial_scope: str
    reason_to_investigate: str
    provenance: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class DesignHypothesis:
    hypothesis_id: str
    statement: str
    direction: str
    force_ids: list[str]
    tension_ids: list[str]
    relationship_ids: list[str]
    expected_effect: str
    known_tradeoffs: list[str]
    uncertainty: str
    spatial_scope: str
    status: str = "PROVISIONAL"
    parent_alternative_id: str | None = None
    provenance: dict[str, Any] = field(default_factory=dict)


def _scope(intent: dict[str, Any], alternative: dict[str, Any] | None = None) -> str:
    return str(
        intent.get("spatial_scope")
        or intent.get("provenance", {}).get("spatial_scope")
        or (alternative or {}).get("spatial_scope")
        or "edificacion"
    )


def _intent_text(intent: dict[str, Any]) -> str:
    return " ".join(
        str(item.get("statement", ""))
        for item in intent.get("adopted_intents", [])
    ).strip()


def derive_forces(
    adopted_intent: dict[str, Any],
    knowledge: dict[str, Any] | None = None,
    *,
    spatial_scope: str | None = None,
) -> list[ArchitecturalForce]:
    scope = spatial_scope or _scope(adopted_intent)
    text = _intent_text(adopted_intent).casefold()
    forces: list[ArchitecturalForce] = []

    def add(force_id: str, description: str, origin: str = "human_intent", evidence: str = "HUMAN_STATED") -> None:
        forces.append(ArchitecturalForce(
            force_id=force_id,
            origin_type=origin,
            description=description,
            spatial_scope=scope,
            epistemic_status=evidence,
            evidence_state=evidence,
            provenance={"source": "HUMAN_INTENT" if origin == "human_intent" else "DESIGN_KNOWLEDGE_MATCH", "intent_project_id": adopted_intent.get("project_id")},
        ))

    if any(term in text for term in ("privacidad", "privacy", "separ", "control")):
        add("FORCE_PRIVACY", "Privacy and degrees of separation may influence spatial organization.")
    if any(term in text for term in ("abierto", "open", "común", "comun", "public")):
        add("FORCE_OPEN_COMMON", "Open/common use may influence access, visibility and shared space.")
    if any(term in text for term in ("compact", "dens", "eficien", "efficient")):
        add("FORCE_COMPACTNESS", "Compact organization may influence adjacency and occupied footprint.")
    if any(term in text for term in ("luz", "daylight", "solar", "patio", "courtyard")):
        add("FORCE_LIGHT", "Access to light or an open void may influence spatial relationships.")

    for link in (knowledge or {}).get("links", [])[:4]:
        kid = link.get("knowledge_item_id") or link.get("pattern_id") or "knowledge-match"
        add(f"FORCE_KNOWLEDGE_{kid}", f"Relevant design knowledge match: {kid}.", "design_knowledge", "SOURCE_DERIVED")

    if not forces:
        add("FORCE_UNSPECIFIED", "The stated intent requires further clarification before a specific force can be asserted.", "human_intent", "REQUIRES_EVIDENCE")
    return forces


def derive_cross_source_contributions(knowledge: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    """Classify source-family contributions without speaking for authors."""
    family_by_source = {
        "BOOK-ALEXANDER-TIMELESS-WAY": "PATTERN_RELATIONAL",
        "BOOK-ALEXANDER-PATTERN-LANGUAGE": "PATTERN_RELATIONAL",
        "BOOK-ALEXANDER-OREGON-EXPERIMENT": "PATTERN_RELATIONAL",
        "CASE-PREVI-LIMA-LAND": "PRECEDENT_CASE",
        "CASE-HOUSES-GENERATED-BY-PATTERNS": "PRECEDENT_CASE",
        "BOOK-CHING-FORM-SPACE-ORDER": "FORM_SPACE_ORDER",
        "BOOK-NEUFERT-ARCHITECTS-DATA": "DIMENSIONAL_FUNCTIONAL",
        "BOOK-WHITE-SITE-ANALYSIS": "SITE_ANALYSIS",
    }
    grouped: dict[str, list[str]] = {}
    for item in (knowledge or {}).get("applicable_items", []):
        source_id = str(item.get("source_id", ""))
        family = family_by_source.get(source_id)
        if family:
            grouped.setdefault(family, []).append(str(item.get("knowledge_item_id")))
    contributions = []
    labels = {
        "PATTERN_RELATIONAL": "relational/process question",
        "FORM_SPACE_ORDER": "form, space and organization question",
        "DIMENSIONAL_FUNCTIONAL": "dimensional/functional reference question",
        "PRECEDENT_CASE": "precedent context question",
        "SITE_ANALYSIS": "site/context analysis question",
    }
    for family, item_ids in sorted(grouped.items()):
        contributions.append({
            "family": family,
            "item_ids": item_ids,
            "contribution": labels[family],
            "epistemic_status": "SOURCE_METADATA_ONLY" if family == "DIMENSIONAL_FUNCTIONAL" else "SOURCE_DERIVED_OR_STRUCTURED_INTERPRETATION",
            "relationship_type": "COMPLEMENTS",
            "basis": "shared contextual retrieval; not authorial consensus",
            "provenance": {"source": "DESIGN_KNOWLEDGE_RETRIEVAL", "human_review_required": True},
        })
    return contributions


def derive_tensions(forces: list[ArchitecturalForce], *, spatial_scope: str, context: str = "") -> list[ArchitecturalTension]:
    ids = {force.force_id for force in forces}
    tensions: list[ArchitecturalTension] = []
    pairs = [
        ("FORCE_PRIVACY", "FORCE_OPEN_COMMON", "Privacy and openness may require different degrees of access and visibility."),
        ("FORCE_COMPACTNESS", "FORCE_LIGHT", "Compactness and access to light may influence different spatial organizations."),
        ("FORCE_PRIVACY", "FORCE_LIGHT", "Separation and daylight access may affect placement and voids."),
    ]
    for index, (left, right, reason) in enumerate(pairs, start=1):
        if left in ids and right in ids:
            tensions.append(ArchitecturalTension(
                tension_id=f"TENSION-{index:02d}",
                force_ids=[left, right],
                why_it_may_exist=reason,
                context=context or "Pilot project context",
                spatial_scope=spatial_scope,
                derivation="SIMS_DEI_DERIVED_INTERPRETATION",
                epistemic_status="SIMS_DEI_DERIVED_INTERPRETATION",
                provenance={"source": "FORCE_SET", "automatic_resolution": False},
            ))
    return tensions


def derive_spatial_relationships(
    alternative: dict[str, Any] | None,
    forces: list[ArchitecturalForce],
    *,
    spatial_scope: str,
) -> list[SpatialRelationship]:
    relationships: list[SpatialRelationship] = []
    params = (alternative or {}).get("parameters", {})
    elements = (alternative or {}).get("representation", {}).get("elements", [])
    if params or elements:
        relationships.append(SpatialRelationship(
            relationship_id="REL-OPEN-COMMON-TO-MASS",
            relationship_type="CONNECTED_TO",
            subject="OPEN_COMMON_SPACE",
            object="BUILDING_MASS",
            spatial_scope=spatial_scope,
            reason_to_investigate="Inspect how shared/open space relates to the occupied mass without prescribing geometry.",
            provenance={"source": "EXISTING_SPATIAL_REPRESENTATION", "element_count": len(elements), "parameter_keys": sorted(params)},
        ))
    if any(force.force_id == "FORCE_PRIVACY" for force in forces):
        relationships.append(SpatialRelationship(
            relationship_id="REL-PRIVATE-FROM-COMMON",
            relationship_type="SEPARATE_FROM",
            subject="PRIVATE_ZONE",
            object="OPEN_COMMON_SPACE",
            spatial_scope=spatial_scope,
            reason_to_investigate="Explore degrees of separation and access rather than enforcing a fixed layout.",
            provenance={"source": "SIMS_DEI_DERIVED_INTERPRETATION"},
        ))
    return relationships


def generate_hypotheses(
    forces: list[ArchitecturalForce],
    tensions: list[ArchitecturalTension],
    relationships: list[SpatialRelationship],
    *,
    spatial_scope: str,
    parent_alternative_id: str | None = None,
) -> list[DesignHypothesis]:
    force_ids = [force.force_id for force in forces]
    tension_ids = [tension.tension_id for tension in tensions]
    relationship_ids = [rel.relationship_id for rel in relationships]
    base = {
        "force_ids": force_ids,
        "tension_ids": tension_ids,
        "relationship_ids": relationship_ids,
        "spatial_scope": spatial_scope,
        "parent_alternative_id": parent_alternative_id,
        "provenance": {"source": "SIMS_DEI_DERIVED_INTERPRETATION", "status": "PROVISIONAL", "decision_created": False},
    }
    return [
        DesignHypothesis(hypothesis_id="HYPOTHESIS-A", statement="Prioritize a compact organization while preserving a legible shared/open area.", direction="COMPACT_WITH_SHARED_VOID", expected_effect="More direct adjacency and an explicit shared void.", known_tradeoffs=["May reduce separation or daylight opportunities depending on geometry."], uncertainty="Requires spatial evaluation and human inspection.", **base),
        DesignHypothesis(hypothesis_id="HYPOTHESIS-B", statement="Prioritize a courtyard/void strategy to mediate privacy and common use.", direction="COURTYARD_MEDIATED", expected_effect="A more explicit relationship between private edges and shared open space.", known_tradeoffs=["May increase circulation or reduce compactness."], uncertainty="Courtyard performance is not inferred without project-specific evaluation.", **base),
        DesignHypothesis(hypothesis_id="HYPOTHESIS-C", statement="Prioritize articulated masses with separated spatial zones.", direction="SEPARATED_ARTICULATED_MASSES", expected_effect="Greater separation between zones and multiple spatial approaches.", known_tradeoffs=["May increase fragmentation and circulation complexity."], uncertainty="Current deterministic geometry may express only a bounded approximation.", **base),
    ]


def build_semantic_reasoning(
    adopted_intent: dict[str, Any],
    knowledge: dict[str, Any] | None = None,
    alternative: dict[str, Any] | None = None,
    *,
    spatial_scope: str | None = None,
    context: str = "",
) -> dict[str, Any]:
    scope = spatial_scope or _scope(adopted_intent, alternative)
    forces = derive_forces(adopted_intent, knowledge, spatial_scope=scope)
    tensions = derive_tensions(forces, spatial_scope=scope, context=context)
    relationships = derive_spatial_relationships(alternative, forces, spatial_scope=scope)
    cross_source_contributions = derive_cross_source_contributions(knowledge)
    hypotheses = generate_hypotheses(forces, tensions, relationships, spatial_scope=scope, parent_alternative_id=(alternative or {}).get("alternative_id"))
    return {
        "spatial_scope": scope,
        "forces": [asdict(item) for item in forces],
        "tensions": [asdict(item) for item in tensions],
        "spatial_relationships": [asdict(item) for item in relationships],
        "cross_source_contributions": cross_source_contributions,
        "hypotheses": [asdict(item) for item in hypotheses],
        "human_confirmation_required": True,
        "decision_created": False,
        "recommendation_created": False,
        "provenance": {"source": "SIMS_DEI_SEMANTIC_REASONING", "interpretation_only": True, "human_authority_preserved": True},
    }


__all__ = ["ArchitecturalForce", "ArchitecturalTension", "SpatialRelationship", "DesignHypothesis", "build_semantic_reasoning", "derive_forces", "derive_tensions", "derive_spatial_relationships", "generate_hypotheses", "derive_cross_source_contributions"]
