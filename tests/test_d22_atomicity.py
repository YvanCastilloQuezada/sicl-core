from __future__ import annotations

import pytest

from sicl.derivation import DerivationLedger, DerivationRecord, TypedRelation, VersionedRef
from sicl.repository import SQLiteRepository


def _record(record_id: str, output_id: str) -> DerivationRecord:
    output = VersionedRef("Area", output_id, 1)
    source = VersionedRef("Geometry", "G1", 1)
    return DerivationRecord(
        record_id,
        output,
        (source,),
        "controlled_method",
        "1.0",
        (TypedRelation(output, source, "COMPUTED_FROM", "COMPUTATIONAL"),),
    )


class _FailOnSecondInsertRepository(SQLiteRepository):
    def __init__(self, path):
        self._insert_count = 0
        super().__init__(path)

    def _insert_event(self, event):
        self._insert_count += 1
        if self._insert_count == 2:
            raise RuntimeError("simulated second-write failure")
        return super()._insert_event(event)


def test_ledger_publish_failure_rolls_back_entire_batch(tmp_path):
    db_path = tmp_path / "atomicity.sqlite"
    store = _FailOnSecondInsertRepository(db_path)
    ledger = DerivationLedger(store)
    records = [_record("D1", "A1"), _record("D2", "A2")]
    with pytest.raises(RuntimeError, match="second-write"):
        ledger.record_batch("P1", records, actor="ARCHI_D2")
    store.close()

    reopened = SQLiteRepository(db_path)
    try:
        assert reopened.events("P1") == []
        assert DerivationLedger(reopened).list("P1") == []
    finally:
        reopened.close()


def test_record_batch_is_idempotent_for_already_published_records(tmp_path):
    store = SQLiteRepository(tmp_path / "idempotent.sqlite")
    ledger = DerivationLedger(store)
    record = _record("D1", "A1")
    try:
        assert ledger.record_batch("P1", [record], actor="ARCHI_D2") == [record]
        assert ledger.record_batch("P1", [record], actor="ARCHI_D2") == []
        assert ledger.list("P1") == [record]
    finally:
        store.close()
