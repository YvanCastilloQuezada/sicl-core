# D-2 Architectural Capability and Contract Notes

## D-1 v1.4 alignment

The D-2 transaction exposes one production mutation path: `ArchiTransaction.apply_full_chain(...)`. It executes the ordered A-002 → H-002 → H-003 → H-004 → H-005 chain and publishes only after the atomic ledger boundary and IFC export succeed.

The former `ArchiTransaction.apply(...)` shortcut was removed because it could mutate canonical state without the required gates. This is an implementation alignment with D-1 v1.4, not a contract revision.

`MutationStatus` is machine-readable. In addition to `BLOCKED`, `FAILED`, and `APPLIED`, the transaction distinguishes `NEEDS_REVIEW`, `INVALID`, `UNKNOWN`, `ESCALATE`, and `REQUIRES_AUTHORITY`. H-004 provenance retains both the complete H-003 report and the eligible/ineligible action partition.

Replay returns `REPLAY_NO_DOUBLE_APPLICATION` with `derivation_recorded=False`, because the replay did not record a new derivation.

## IFC identity

`IfcGlobalId.from_archi_id()` deterministically compresses the first 128 bits of the SHA-256-based `ArchiElementId` using IfcOpenShell's standard IFC GUID compression. It does not use time, randomness, or geometry, so geometry changes preserve identity.

## Geometry capability boundary

The `GeometryKind` enum declares `EXTRUDED_RECTANGLE` and `EXTRUDED_CIRCLE`. The current IFC exporter implements only `EXTRUDED_RECTANGLE`. `EXTRUDED_CIRCLE` is a declared future capability, not an implemented one; export fails closed with `GEOMETRY_KIND_NOT_IMPLEMENTED` rather than silently producing an incorrect IFC.

## IFC publication boundary

`ArchiTransaction` serializes IFC to memory first. When an external `ifc_path` is requested, bytes are written to a sibling staging file and promoted with a reversible backup. Ledger publication follows promotion; if the atomic ledger batch fails, the previous IFC is restored or a newly promoted file is removed. If staging or promotion fails, the ledger and canonical state remain untouched. `ifc_path=None` never creates a filesystem artifact.

## Dependency version semantics

`ArchiElement.semantic_dict()` includes `hosted_in_version` and `contained_in_version` when the corresponding relationship is present. A dependent recomputed against host version 2 therefore has a different deterministic semantic hash from the same dependent hosted in version 1.
