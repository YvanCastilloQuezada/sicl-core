import pytest

from sicl.multiscale_generative import capability_matrix, cross_scale_context, resolve_generative_capabilities


def test_exact_eleven_scopes_have_truthful_profiles():
    matrix = capability_matrix()
    assert len(matrix) == 11
    assert {item["spatial_scope"] for item in matrix} == {"pais", "macro_region", "region", "provincia_metropoli", "distrito_ciudad", "zona_barrio_sector", "parcela_sitio", "edificacion", "sistema", "espacio", "objeto"}
    assert next(item for item in matrix if item["spatial_scope"] == "edificacion")["capability_state"] == "AVAILABLE"
    assert next(item for item in matrix if item["spatial_scope"] == "objeto")["capability_state"] == "NOT_AVAILABLE"


def test_scope_changes_operations_and_data_state():
    building = resolve_generative_capabilities("edificacion")
    country = resolve_generative_capabilities("pais")
    assert building["capabilities"]["generate"] != country["capabilities"]["generate"]
    assert "TERRITORIAL_DATA" in country["missing_data"]
    assert building["camera_zoom_is_not_scope"] is True


def test_cross_scale_context_never_fabricates_containment():
    result = cross_scale_context("parcela_sitio", "SITE-A", "edificacion", "BUILDING-A")
    assert result["relationship"] == "DERIVED_WITH_CONTEXT_FROM"
    assert result["containment_asserted"] is False
    with pytest.raises(ValueError, match="'invalid_scope'"):
        cross_scale_context("invalid_scope", "P", "objeto", "O")
