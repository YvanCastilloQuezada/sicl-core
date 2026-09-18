from sicl.candidate_normalization import normalize_design_candidate


def test_p3_spatial_candidate_is_adapted_to_canonical_alternative():
    candidate = {
        "family": "COURTYARD",
        "representation": {
            "alternative_id": "UPAO-001-P3-1",
            "seed": "P3:COURTYARD",
            "elements": [],
        },
        "lineage": {"operation": "GENERATE_SPACE_LAYOUT"},
    }

    normalized = normalize_design_candidate(candidate, "UPAO-001")

    assert normalized["alternative_id"] == "UPAO-001-P3-1"
    assert normalized["project_id"] == "UPAO-001"
    assert normalized["parameters"]["strategy"] == "courtyard"
    assert normalized["source"] == "GDI-P3-ADAPTER"
    assert "representation" not in normalized


def test_canonical_alternative_passes_through_without_duplication():
    canonical = {
        "alternative_id": "UPAO-001-A",
        "project_id": "UPAO-001",
        "name": "COMPACT",
        "parameters": {"strategy": "compact", "footprint_ratio": 0.42, "floors": 4},
        "status": "GENERATED",
        "version": 1,
        "source": "UPAO-001",
    }

    assert normalize_design_candidate(canonical, "UPAO-001") is canonical
