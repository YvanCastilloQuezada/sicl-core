"""Catalog boundary for planning instruments.

The RFC-008 structure is intentionally empty: no real planning instruments are
loaded until the Product Owner authorizes a verified corpus.
"""

INSTRUMENTS: dict[str, dict] = {}


def catalog_instruments() -> list[dict]:
    return list(INSTRUMENTS.values())
