from __future__ import annotations

from dataclasses import replace

import pytest

from sicl.optimization import pareto_front
from sicl.spatial_generator import UPAO001SpatialGenerator, generate_upao001_alternatives
from sicl.spatial_evaluation import (
    AREA_UNIT,
    GROSS_MASSING_AREA,
    OPEN_SITE_AREA,
    SpatialEvaluationIncomplete,
    build_upao001_dataset,
    canonical_objectives,
    open_site_area,
    spatial_metrics,
)


def representations():
    generator = UPAO001SpatialGenerator()
    return tuple(generator.generate(item, seed="S6-P0.1") for item in generate_upao001_alternatives())


def test_canonical_dataset_has_exactly_six_records_and_ids():
    dataset = build_upao001_dataset(representations())
    assert len(dataset.evaluations) == 6
    assert {item.alternative_id for item in dataset.evaluations} == {
        "UPAO-001-A", "UPAO-001-B", "UPAO-001-C"
    }
    assert {item.objective_id for item in dataset.evaluations} == {
        "OBJ-GROSS-MASSING-AREA", "OBJ-OPEN-SITE-AREA"
    }
    assert all(item.unit == "m²" for item in dataset.evaluations)
    assert all(item.source == "SIMULATION" for item in dataset.evaluations)
    assert all(item.alternative_id.startswith("UPAO-001-") for item in dataset.evaluations)
    assert not any(item.alternative_id in {"ALT-1", "ALT-A"} for item in dataset.evaluations)


def test_authorized_objectives_are_maximize_m2_only():
    objectives = canonical_objectives()
    assert [item.key for item in objectives] == [GROSS_MASSING_AREA, OPEN_SITE_AREA]
    assert [item.direction for item in objectives] == ["MAXIMIZE", "MAXIMIZE"]
    assert [item.value for item in objectives] == ["m²", "m²"]


def test_open_site_area_is_exact_difference_and_missing_is_incomplete():
    assert open_site_area({"site_area": 100.0, "footprint_area": 42.5}) == 57.5
    assert open_site_area({"footprint_area": 42.5}) is None
    assert open_site_area({"site_area": 100.0}) is None
    assert open_site_area({"site_area": "100", "footprint_area": 42.5}) is None
    assert open_site_area({"site_area": 10.0, "footprint_area": 11.0}) is None


def test_values_are_derived_from_s2_and_repeatable():
    first = build_upao001_dataset(representations())
    second = build_upao001_dataset(representations())
    first_values = [(item.alternative_id, item.objective_id, item.value) for item in first.evaluations]
    second_values = [(item.alternative_id, item.objective_id, item.value) for item in second.evaluations]
    assert first_values == second_values
    assert first.pareto == second.pareto
    for alternative_id, metrics in first.metrics.items():
        assert metrics["open_site_area"] == metrics["site_area"] - metrics["footprint_area"]
        assert metrics["gross_massing_area"] > 0
        assert metrics["open_site_area"] > 0


def test_raw_pareto_accepts_dataset_and_preserves_canonical_ids():
    dataset = build_upao001_dataset(representations())
    assert set(dataset.pareto.non_dominated) | set(dataset.pareto.dominated) == {
        "UPAO-001-A", "UPAO-001-B", "UPAO-001-C"
    }
    assert dataset.pareto.incomplete == []
    assert not dataset.decision_created
    assert not dataset.recommendation_created
    assert not dataset.human_review_created


def test_incomplete_s2_metrics_never_substitute_zero(monkeypatch):
    class MissingMetrics:
        def metrics(self, _representation):
            return {"site_area": 100.0, "footprint_area": None, "gross_massing_area": 10.0}

    with pytest.raises(SpatialEvaluationIncomplete):
        spatial_metrics(representations()[0], generator=MissingMetrics())


def test_noncanonical_order_or_ids_are_rejected():
    reps = representations()
    with pytest.raises(ValueError, match="ordered as canonical"):
        build_upao001_dataset((reps[1], reps[0], reps[2]))
    with pytest.raises(ValueError, match="ordered as canonical"):
        build_upao001_dataset((replace(reps[0], alternative_id="ALT-A"), reps[1], reps[2]))


def test_feasible_pareto_is_not_called_or_created():
    dataset = build_upao001_dataset(representations())
    assert not hasattr(dataset, "feasible_pareto_front")
    assert dataset.pareto is not None


def test_provenance_is_explicitly_educational_and_synthetic():
    dataset = build_upao001_dataset(representations())
    assert dataset.provenance == ("SYNTHETIC", "DETERMINISTIC_DERIVED", "EDUCATIONAL")
    assert all(item.confidence == 1.0 for item in dataset.evaluations)
