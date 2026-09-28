from sicl.archi import ArchiElement, ArchiElementId, ArchiGeometry, ElementKind, GeometryKind, ProfileSpec
from sicl.derivation import DerivationLedger, DerivationRecord, TypedRelation, VersionedRef
from sicl.h005 import RecomputationRegistry


class MemoryStore:
    def __init__(self):
        self.items = []

    def add_event(self, event):
        self.items.append(event)
        return event

    def add_events_atomic(self, events):
        self.items.extend(events)
        return list(events)

    def events(self, project_id=None):
        return [event for event in self.items if project_id is None or event.project_id == project_id]


def setup_chain():
    wall = ArchiElement(
        ArchiElementId.compute("P", "WALL", "w"), "P", ElementKind.WALL,
        ArchiGeometry(GeometryKind.EXTRUDED_RECTANGLE, ProfileSpec(200, 100), height_mm=2800),
    )
    door = ArchiElement(
        ArchiElementId.compute("P", "DOOR", "d"), "P", ElementKind.DOOR,
        wall.geometry, hosted_in=wall.element_id,
    )
    space = ArchiElement(
        ArchiElementId.compute("P", "SPACE", "a"), "P", ElementKind.SPACE,
        wall.geometry,
    )
    ledger = DerivationLedger(MemoryStore())
    old = wall.ref()
    door_old = VersionedRef("DOOR", door.element_id.value, 1, "b" * 64)
    space_old = VersionedRef("SPACE", space.element_id.value, 1, "c" * 64)
    ledger.record("P", DerivationRecord(
        "D-01", door_old, (old,), "archi.door.recompute", "1.0",
        (TypedRelation(door_old, old, "DERIVED_FROM", "ARCHITECTURAL"),),
    ))
    ledger.record("P", DerivationRecord(
        "A-01", space_old, (old,), "archi.space.recompute", "1.0",
        (TypedRelation(space_old, old, "DERIVED_FROM", "ARCHITECTURAL"),),
    ))
    registry = RecomputationRegistry()

    def make_output(previous, refs, entity_type, entity_id, content_hash):
        current = refs[old.key()]
        output = VersionedRef(entity_type, entity_id, previous.output.version + 1, content_hash)
        return DerivationRecord(
            previous.id + "-R", output, (current,), previous.method, previous.method_version,
            (TypedRelation(output, current, "DERIVED_FROM", "ARCHITECTURAL"),),
        )

    registry.register(
        "archi.door.recompute", "1.0",
        lambda project, record, refs: make_output(record, refs, "DOOR", door.element_id.value, "d" * 64),
    )
    registry.register(
        "archi.space.recompute", "1.0",
        lambda project, record, refs: make_output(record, refs, "SPACE", space.element_id.value, "e" * 64),
    )
    refs = {old.key(): old}
    return wall, door, space, ledger, registry, refs
