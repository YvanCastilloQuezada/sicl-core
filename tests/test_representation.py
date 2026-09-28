from dataclasses import FrozenInstanceError

import pytest

from sicl.representation import (
    AnnotationProfile,
    DiagnosticCode,
    ExchangeRole,
    Freshness,
    GraphicEntity,
    GraphicScene,
    GraphicStyle,
    GraphicTrace,
    ProfileKind,
    RepresentationError,
    RepresentationProfile,
    SourceAuthority,
    SourceConflictError,
    SourceSnapshot,
    ViewDefinition,
    ViewFamily,
    ViewType,
    build_scene,
    detect_source_conflict,
    evaluate_freshness,
)

HASH_A = "a" * 64
HASH_B = "b" * 64


def source(authority=SourceAuthority.CANONICAL_SOURCE, version="1", digest=HASH_A, freshness=Freshness.CURRENT, **kwargs):
    return SourceSnapshot("MODEL-1", "D2", version, digest, authority, freshness=freshness, **kwargs)


def contracts(source_snapshot=None):
    src = source_snapshot or source()
    view = ViewDefinition("VIEW-1", ViewType.ARCHITECTURAL_PLAN, ViewFamily.GEOMETRIC, "PROJECT-1")
    profile = RepresentationProfile("PROFILE-1", ProfileKind.CONCEPTUAL, ViewFamily.GEOMETRIC)
    style = GraphicStyle("STYLE-1", line_weights={"cut": "0.70"})
    annotation = AnnotationProfile("ANNOT-1", room_labels=True)
    return src, view, profile, style, annotation


def entity():
    return GraphicEntity(
        "G-1",
        "wall-outline",
        {"kind": "line", "coordinates": ((0.0, 0.0), (1.0, 0.0))},
        GraphicTrace(("WALL-1",), "wall", "EXTRACTION", "1", HASH_A),
        style_ref="STYLE-1",
    )


def test_canonical_source_is_accepted_and_scene_is_read_only():
    src, view, profile, style, annotation = contracts()
    scene = build_scene(src, view, profile, style, annotation, "transform-1", entities=(entity(),))
    assert isinstance(scene, GraphicScene)
    assert scene.source_snapshot.authority is SourceAuthority.CANONICAL_SOURCE
    assert scene.entities[0].trace.source_entity_refs == ("WALL-1",)
    with pytest.raises(FrozenInstanceError):
        scene.transform_version = "changed"


def test_derived_source_retains_provenance_and_current_freshness():
    canonical = source()
    derived = source(SourceAuthority.DERIVED_SOURCE, freshness=Freshness.UNKNOWN)
    assert derived.source_id == canonical.source_id
    assert derived.authority is SourceAuthority.DERIVED_SOURCE
    assert evaluate_freshness(derived, canonical) is Freshness.CURRENT


def test_derived_source_stale_is_blocked():
    stale = source(SourceAuthority.DERIVED_SOURCE, version="1", digest=HASH_A, freshness=Freshness.STALE)
    _, view, profile, style, annotation = contracts(stale)
    with pytest.raises(RepresentationError, match="STALE_SOURCE"):
        build_scene(stale, view, profile, style, annotation, "transform-1")


def test_unknown_freshness_is_explicit_not_silent_fallback():
    unknown = source(freshness=Freshness.UNKNOWN)
    src, view, profile, style, annotation = contracts(unknown)
    scene = build_scene(src, view, profile, style, annotation, "transform-1")
    assert DiagnosticCode.MISSING_REQUIRED_EVIDENCE in scene.diagnostics
    assert scene.entities == ()


def test_exchange_source_requires_declared_role_and_never_becomes_canonical():
    with pytest.raises(RepresentationError):
        SourceSnapshot("IFC-1", "IFC", "1", HASH_A, SourceAuthority.EXCHANGE_SOURCE)
    exchange = SourceSnapshot(
        "IFC-1", "IFC", "1", HASH_A, SourceAuthority.EXCHANGE_SOURCE,
        exchange_role=ExchangeRole.REFERENCE_IMPORT,
    )
    assert exchange.authority is SourceAuthority.EXCHANGE_SOURCE
    assert exchange.exchange_role is ExchangeRole.REFERENCE_IMPORT


def test_same_identity_and_version_with_incompatible_fingerprint_conflicts():
    left = source(digest=HASH_A)
    right = source(digest=HASH_B)
    assert detect_source_conflict(left, right)
    with pytest.raises(SourceConflictError, match="SOURCE_CONFLICT"):
        from sicl.representation import require_no_source_conflict
        require_no_source_conflict(left, right)


def test_different_source_identity_is_unknown_freshness_not_conflict():
    other = SourceSnapshot("OTHER", "D2", "2", HASH_B, SourceAuthority.CANONICAL_SOURCE)
    assert not detect_source_conflict(source(), other)
    derived = source(SourceAuthority.DERIVED_SOURCE, version="2", digest=HASH_B)
    assert evaluate_freshness(derived, other) is Freshness.UNKNOWN


def test_style_mappings_are_immutable():
    style = GraphicStyle("STYLE", line_weights={"cut": "0.70"})
    with pytest.raises(TypeError):
        style.line_weights["cut"] = "0.18"


def test_scene_fingerprint_is_deterministic_across_mapping_order():
    src, view, profile, _, annotation = contracts()
    first_style = GraphicStyle("STYLE", line_weights={"cut": "0.70", "thin": "0.18"})
    second_style = GraphicStyle("STYLE", line_weights={"thin": "0.18", "cut": "0.70"})
    first = build_scene(src, view, profile, first_style, annotation, "transform-1")
    second = build_scene(src, view, profile, second_style, annotation, "transform-1")
    assert first.scene_fingerprint == second.scene_fingerprint
    assert first.scene_id == second.scene_id


def test_scene_fingerprint_changes_when_transform_changes():
    src, view, profile, style, annotation = contracts()
    first = build_scene(src, view, profile, style, annotation, "transform-1")
    second = build_scene(src, view, profile, style, annotation, "transform-2")
    assert first.scene_fingerprint != second.scene_fingerprint


def test_scene_fingerprint_changes_when_graphic_entity_changes():
    src, view, profile, style, annotation = contracts()
    first = build_scene(src, view, profile, style, annotation, "transform-1")
    changed = GraphicEntity(
        "G-2", "wall-outline", {"kind": "line", "coordinates": ((0.0, 0.0), (2.0, 0.0))},
        entity().trace, style_ref="STYLE-1",
    )
    second = build_scene(src, view, profile, style, annotation, "transform-1", entities=(changed,))
    assert first.scene_fingerprint != second.scene_fingerprint


def test_graphic_scene_is_not_a_viewport_sheet_or_svg_payload():
    src, view, profile, style, annotation = contracts()
    scene = build_scene(src, view, profile, style, annotation, "transform-1")
    assert not hasattr(scene, "viewports")
    assert not hasattr(scene, "paper")
    assert not hasattr(scene, "svg")


def test_section_requires_cut_plane_evidence():
    with pytest.raises(RepresentationError, match="cut_plane"):
        ViewDefinition("SECTION-1", ViewType.SECTION, ViewFamily.GEOMETRIC, "PROJECT-1")


def test_invalid_source_fingerprint_is_rejected():
    with pytest.raises(RepresentationError, match="SHA-256"):
        source(digest="not-a-hash")


def test_non_finite_graphic_geometry_is_rejected():
    with pytest.raises(RepresentationError, match="finite"):
        GraphicEntity("G", "line", {"x": float("nan")}, entity().trace)


def test_profile_is_separate_from_view_definition():
    src, view, profile, style, annotation = contracts()
    assert view.view_type is ViewType.ARCHITECTURAL_PLAN
    assert profile.kind is ProfileKind.CONCEPTUAL
    assert view.view_type != profile.kind
    scene = build_scene(src, view, profile, style, annotation, "transform-1")
    assert scene.view.view_id == "VIEW-1"
    assert scene.representation_profile.profile_id == "PROFILE-1"


def test_source_metadata_is_frozen_recursively():
    snapshot = source(freshness=Freshness.CURRENT, metadata={"nested": {"key": "value"}})
    with pytest.raises(TypeError):
        snapshot.metadata["nested"]["key"] = "changed"
