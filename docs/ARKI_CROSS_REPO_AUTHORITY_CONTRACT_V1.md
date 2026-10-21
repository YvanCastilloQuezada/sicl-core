# ARKI Cross-Repository Authority Contract V1

**State:** CONTRACT / IMPLEMENTATION RECONCILIATION  
**Date:** 2026-10-07  
**Repositories:** `sicl-core` + `sicl-web`

## 1. Purpose

Prevent parallel truths while ARKI integrates professional development (F7) and dossier generation (F8).

## 2. Authority law

| Surface | Authority |
|---|---|
| Canonical Project State, evidence, provenance, governed decisions | `sicl-core / CORE` |
| Architectural semantic truth | `D-2` |
| Operational Geometry | `AGK` |
| Professional discipline models in `sicl-web` | derived projections / analysis |
| F8 technical dossier | derived publication/delivery projection |
| Capability Fabric | noncanonical execution/provider boundary |
| ACS | acquisition/experimentation/evidence; noncanonical |

A projection may reference canonical state. It may not silently replace it.

## 3. Required cross-repository references

An F7 professional state must preserve, at minimum:

- `projectId`
- Core Project State reference/revision
- D-2 semantic-state reference
- AGK operational-state reference
- source BASELINE_0 fingerprint where imported/existing-project evidence is involved
- professional projection provenance
- explicit UNKNOWN/open issues
- Human Authority acceptance evidence before F8 consumption

All project references must identify the same project. Cross-project authority drift fails closed.

## 4. Mutation rule

`sicl-web` analysis, BIM, coordination, cost and dossier surfaces are not authorized to mutate canonical Core state merely by producing a result. Promotion/commit requires the governed Core/D-2/AGK path appropriate to the mutation.

## 5. F7/F8 rule

F7 may assemble a coordinated professional state only as a traceable projection over canonical references. F8 may consume only an accepted F7 state and must preserve the F7/Core/D-2/AGK lineage. Exported IFC/CAD/PDF/dossier artifacts are not canonical truth.

## 6. Evidence boundary

The corresponding TypeScript authority-reference enforcement is implemented on the `sicl-web` branch `feat/f7-f8-integral-closure`. This document does not claim that branch VERIFIED until its execution gate passes.

## 7. Zero-debt rule

Any reproducible path that permits a web projection, adapter, dossier, Capability Fabric provider or ACS result to silently establish a competing canonical Project State, architectural semantic truth or Operational Geometry truth is a blocking defect.
