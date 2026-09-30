# [6.11] Core Promotion Concurrency Guarantee

Status: IMPLEMENTATION AUTHORIZED — CONTROLLED GATES

## 1. Identity
- Block: [6.11] CORE IMPLEMENTATION
- Purpose: make DeveloperProposal promotion concurrency-safe, idempotent, auditable, and fail-closed.

## 2. Baselines
- Core main baseline: 45fd21a6b41f67e2d25bffac1f8b7e236cc6555e
- Web main baseline: 47c4f9077a0e237412e507d4b4c0e0bae5f546b1
- Web PR #30: merged and post-merge verified before this Core block.

## 3. Applicable frozen contract
- [6.7-T630-C.1] V1.4 amended.
- RUA-C4-05.
- 503/500 envelope V1 amendment.
- Frozen Web contract is not reopened by this Core implementation.

## 3.1 Error wire materialization
- RETRIABLE_BUSY_EXHAUSTED -> HTTP 503.
- HTTP 503 RETRIABLE_BUSY_EXHAUSTED MUST emit Retry-After: 1.
- INTEGRITY_FAILURE -> HTTP 500.
- Successful first commit -> data.status COMMITTED.
- Successful idempotent replay -> data.status ALREADY_COMMITTED.
- Ordinary promotion rejection semantics remain unchanged.

## 4. Approved implementation sequence
- [6.11.1] Preflight — PASS WITH CORRECTION.
- [6.11.2] Branch and documentation baseline — this step.
- [6.11.3] Event Store inspection / implementation gate.
- [6.11.4] Schema changes.
- [6.11.5] Atomic migration.
- [6.11.6] ledger_binding_guard.
- [6.11.7] developer_promotion concurrency changes.
- [6.11.8] Error wire.
- [6.11.9] TC-1..TC-24.
- [6.11.10] TC-WIRE-1..5.
- [6.11.11] Repeat T-MIG + T-U11 + T-6.30 + E-R.
- [6.11.12] Full Core suite/build gates applicable to the repository.
- [6.11.13] Code inspection.
- [6.11.14] CI on exact feature SHA.
- [6.11.15] CI inspection.
- [6.11.16] Protected merge gate.
- [6.11.17] Verify Core main.
- [6.11.18] Real post-merge CI.
- [6.11.19] Zero-debt closure.

## 5. Four mandatory execution conditions
1. Preflight the exact baseline and key files before functional modification.
2. Reuse the existing DEVELOPER_PROMOTION_COMMITTED event. Do not duplicate, rename, or reinterpret it.
3. Benchmark ledger_binding_guard with more than 100,000 synthetic d2_snapshots and record reproducible performance evidence.
4. TC-24 must prove BUSY and STALE_BASE_VERSION consume one shared monotonic deadline; retries must never reset or extend it.

## 6. Approved plan corrections
- A1: _already_committed is in src/sicl/developer_promotion.py, not repository.py.
- A2: DEVELOPER_PROMOTION_COMMITTED already exists and must be reused.
- A3: TC-7 is a reproducible isolated SQLite benchmark with 100,001+ synthetic snapshots; record per-insert timing, median, max, P95/P99 and environment. Performance must not degrade as a function of snapshot position/count.
- A4: source schema is verified legacy; runtime DB PRAGMA user_version remains UNOBSERVED until an actual DB is opened. Never convert UNOBSERVED into 0.

## 7. Implementation invariants
- No Web changes.
- No unrelated Core changes.
- No merge without CI on the exact final feature SHA.
- No green claim without evidence.
- No silent repair, inference, deduplication, or fabricated runtime state.
- No archived technical debt at closure.
- SIMULATED != OBSERVED != FACT.
- UNKNOWN remains UNKNOWN until evidence resolves it.

## 7.1 Retry and integrity materialization
The following values and behaviors materialize the V1.4 concurrency contract in Core:

- PROMOTION_DEADLINE_MS = 5000.
- BUSY_TIMEOUT_CAP_MS = 1000; each attempt MUST also be bounded by the remaining shared deadline.
- SAFETY_MAX_ATTEMPTS = 100.
- BACKOFF_BASE_MS = 50, BACKOFF_FACTOR = 2, BACKOFF_CAP_MS = 500.
- Retry backoff is deterministic; JITTER = NO.
- BUSY, SQLITE_LOCKED, and STALE_BASE_VERSION consume the same monotonic deadline. No retry may reset or extend it.
- Every STALE_BASE_VERSION retry MUST reread the authoritative current D-2, recompute based_on_version, revalidate creation, and rebuild the candidate snapshot. Attempt-local architectural state MUST NOT be reused.
- The known snapshot race is classified only from the exact SQLite error `UNIQUE constraint failed: d2_snapshots.project_id, d2_snapshots.version`.
- After that exact UNIQUE, authoritative version > based_on_version means STALE_BASE_VERSION; authoritative version <= based_on_version means PROMOTION_SNAPSHOT_UNIQUE_INTEGRITY_FAILURE.
- Unknown IntegrityError variants MUST NOT be silently reclassified as the known snapshot race.
- Startup MUST fail closed for migrated schemas containing invalid D-2 ancestry or inconsistent developer-promotion ledger bindings.
- INTEGRITY_FAILURE is terminal and MUST NOT be retried.
- Reaching SAFETY_MAX_ATTEMPTS is anomalous, MUST emit an ERROR log, and does not replace the monotonic deadline as normal termination authority.
- Materialization decision for the existing public wire: if SAFETY_MAX_ATTEMPTS is reached before the deadline, the promotion terminates as RETRIABLE_BUSY_EXHAUSTED. This output choice is an implementation materialization; it is not represented as recovered historical wording.

## 8. Scope candidates — verify again before functional edits
- src/sicl/repository.py
- src/sicl/developer_promotion.py
- api/routes/v1.py
- directly relevant tests/benchmarks only.

## 9. Hard stop
STOP if the implementation contradicts the frozen contract, requires out-of-scope functional changes, exposes an uncovered migration state, or cannot close a required gate with evidence.

SIN DEUDAS. NUNCA DEUDAS.
