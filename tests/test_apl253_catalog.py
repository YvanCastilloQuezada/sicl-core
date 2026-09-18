from sicl.apl253_catalog import APL253_RECORDS
from sicl.design_knowledge import LicenseStatus, ReviewStatus, list_items


def test_apl253_inventory_is_complete_and_consecutive():
    assert len(APL253_RECORDS) == 253
    assert [number for number, _, _ in APL253_RECORDS] == list(range(1, 254))
    assert len({title for _, title, _ in APL253_RECORDS}) == 253
    assert sum(bool(related) for _, _, related in APL253_RECORDS) == 252


def test_apl253_items_are_metadata_only_and_rights_conservative():
    items = [item for item in list_items() if item["knowledge_item_id"].startswith("ITEM-APL-")]
    assert len(items) == 253
    assert all(item["source_id"] == "BOOK-ALEXANDER-PATTERN-LANGUAGE" for item in items)
    assert all(item["review_status"] == ReviewStatus.UNDER_REVIEW.value for item in items)
    assert all(item["conditions"]["rights_status"] == LicenseStatus.LICENSE_REVIEW_REQUIRED.value for item in items)
    assert all(item["conditions"]["verification_status"] == "PARTIALLY_VERIFIED" for item in items)
    assert all("No se ingirió" in item["limitations"][0] for item in items)
    assert any(item["related_item_ids"] for item in items)
    assert all(item["conditions"]["relationship_source"] == "SOURCE_DERIVED" for item in items)


def test_apl253_items_cover_exact_existing_scales_without_forcing_all_scopes():
    items = [item for item in list_items() if item["knowledge_item_id"].startswith("ITEM-APL-")]
    assert any("pais" in item["applicable_scales"] for item in items)
    assert any("parcela_sitio" in item["applicable_scales"] for item in items)
    assert any("objeto" in item["applicable_scales"] for item in items)
    assert all(len(item["applicable_scales"]) < 11 for item in items)
