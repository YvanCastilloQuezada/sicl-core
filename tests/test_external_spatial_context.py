from sicl.external_spatial_context import build_bounded_overpass_query, fetch_open_meteo_elevation, normalize_overpass_response, query_external_context


def fixture_response():
    return {"elements": [
        {"type": "way", "id": 1, "tags": {"highway": "residential", "name": "Synthetic Road"}, "geometry": [{"lat": -12.0, "lon": -77.0}, {"lat": -12.0, "lon": -76.999}]},
        {"type": "way", "id": 2, "tags": {"building": "yes"}, "geometry": [{"lat": -12.0, "lon": -77.0}, {"lat": -12.0, "lon": -76.999}, {"lat": -12.001, "lon": -76.999}, {"lat": -12.0, "lon": -77.0}]},
        {"type": "node", "id": 3, "tags": {"amenity": "school"}, "lat": -12.0005, "lon": -76.9995},
    ]}


def test_query_requires_bounded_extent_and_scope_aware_window():
    result = query_external_context({"spatial_scope": "parcela_sitio", "latitude": -12.0, "longitude": -77.0, "radius_m": 250, "categories": ["roads"]}, fetcher=lambda query: {"elements": []})
    assert result["state"] == "UNAVAILABLE"
    assert result["query"]["extent"]["units"] == "m"
    assert "way[highway]" in result["query"] or result["query"]["provider"]


def test_overpass_fixture_normalizes_external_features_and_provenance():
    result = query_external_context({"spatial_scope": "distrito_ciudad", "bbox": [-12.01, -77.01, -11.99, -76.99], "categories": ["roads", "buildings", "pois"]}, fetcher=lambda query: fixture_response())
    assert result["state"] == "AVAILABLE"
    assert {feature["properties"]["category"] for feature in result["features"]} == {"roads", "buildings", "pois"}
    assert all(feature["properties"]["epistemic_state"] == "EXTERNAL_SOURCE" for feature in result["features"])
    assert result["provenance"]["provider"] == "OpenStreetMap"
    assert result["provenance"]["license"]


def test_partial_response_and_provider_failure_are_non_fatal():
    partial = query_external_context({"spatial_scope": "zona_barrio_sector", "latitude": -12.0, "longitude": -77.0, "categories": ["roads", "buildings"]}, fetcher=lambda query: {"elements": fixture_response()["elements"][:1]})
    assert partial["state"] == "PARTIAL"
    failed = query_external_context({"spatial_scope": "provincia_metropoli", "latitude": -12.0, "longitude": -77.0, "categories": ["roads"]}, fetcher=lambda query: (_ for _ in ()).throw(RuntimeError("provider unavailable")))
    assert failed["state"] == "UNAVAILABLE"
    assert failed["decision_created"] is False


def test_query_never_creates_canonical_scope_or_regulatory_claim():
    query = build_bounded_overpass_query((-12.01, -77.01, -11.99, -76.99), ["roads", "buildings"])
    assert "[out:json]" in query
    assert "zoning" not in query.lower()
    assert "legal_access" not in query.lower()


def test_elevation_adapter_preserves_external_status_and_not_a_survey():
    result = fetch_open_meteo_elevation(-12.0, -77.0, fetcher=lambda url: {"elevation": 142.5})
    assert result["state"] == "AVAILABLE"
    assert result["elevation_m"] == 142.5
    assert result["surveyed"] is False
    assert result["provider"] == "Open-Meteo"
