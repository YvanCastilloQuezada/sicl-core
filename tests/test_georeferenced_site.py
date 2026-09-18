import io
import zipfile

import pytest

from sicl.georeferenced_site import context_query, local_project_frame, normalize_reference_point, parse_kml, polygon_metrics, site_fit, terrain_query, validate_polygon


KML = b'''<?xml version="1.0"?><kml xmlns="http://www.opengis.net/kml/2.2"><Document><Placemark><name>Site</name><Polygon><outerBoundaryIs><LinearRing><coordinates>-79.0,-8.0,0 -78.999,-8.0,0 -78.999,-7.999,0 -79.0,-7.999,0 -79.0,-8.0,0</coordinates></LinearRing></outerBoundaryIs></Polygon></Placemark></Document></kml>'''


def kmz(payload=KML):
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        archive.writestr("doc.kml", payload)
    return buffer.getvalue()


def test_reference_point_keeps_boundary_unknown():
    point = normalize_reference_point(-79.0, -8.0, human_confirmed=True)
    assert point["human_confirmed"] is True
    assert point["boundary_state"] == "UNKNOWN"
    assert point["crs"] == "EPSG:4326"


def test_valid_kml_polygon_and_kmz_converge_to_same_preview():
    kml = parse_kml(KML, "site.kml")
    archive = parse_kml(kmz(), "site.kmz")
    assert kml["classification"] == "VALID_SINGLE_POLYGON"
    assert archive["classification"] == "VALID_SINGLE_POLYGON"
    assert archive["source"]["archive"]["archive_entries"] == 1


def test_multiple_polygon_and_point_only_are_not_silently_selected():
    multiple = KML.replace(b"</Document>", KML.split(b"<Placemark>")[1].split(b"</Placemark>")[0].join([b"<Placemark>", b"</Placemark>"]) + b"</Document>")
    assert parse_kml(multiple)["classification"] in {"MULTIPLE_POLYGONS", "AMBIGUOUS_SITE_BOUNDARY"}
    point = b'<kml xmlns="http://www.opengis.net/kml/2.2"><Point><coordinates>-79,-8,0</coordinates></Point></kml>'
    assert parse_kml(point)["classification"] == "POINT_ONLY"


def test_invalid_self_intersection_and_unknown_crs_are_explicit():
    bowtie = [[0, 0], [1, 1], [0, 1], [1, 0], [0, 0]]
    result = validate_polygon(bowtie, "EPSG:4326")
    assert result["state"] == "INVALID"
    assert "SELF_INTERSECTION" in result["errors"]
    assert validate_polygon(KML and [[0, 0], [1, 0], [1, 1], [0, 0]], "EPSG:32717")["state"] == "INVALID"


def test_metrics_are_local_metric_not_angular_degrees():
    parsed = parse_kml(KML)
    ring = parsed["geometries"][0]["coordinates"][0]
    metrics = polygon_metrics(ring)
    frame = local_project_frame(ring)
    assert metrics["status"] == "DERIVED"
    assert metrics["units"] == "m"
    assert frame["working_crs"] == "LOCAL_PROJECT_METRIC"
    assert metrics["area_m2"] > 0


def test_kmz_path_traversal_is_rejected():
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        archive.writestr("../evil.kml", KML)
    with pytest.raises(ValueError, match="KMZ_PATH_TRAVERSAL"):
        parse_kml(buffer.getvalue(), "unsafe.kmz")


def test_site_fit_is_geometric_only_and_unknowns_are_preserved():
    site = {"type": "Polygon", "coordinates": [[[0, 0], [10, 0], [10, 10], [0, 10], [0, 0]]]}
    building = {"type": "Polygon", "coordinates": [[[2, 2], [4, 2], [4, 4], [2, 4], [2, 2]]]}
    result = site_fit(site, building)
    assert result["state"] == "INSIDE"
    assert result["buildability"] == "UNKNOWN"
    assert terrain_query()["state"] == "UNAVAILABLE / UNKNOWN"
    assert context_query()["state"] == "UNAVAILABLE / UNKNOWN"
