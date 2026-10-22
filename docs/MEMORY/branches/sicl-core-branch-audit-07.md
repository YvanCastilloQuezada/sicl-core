# SICL Core — auditoría de ramas (lote 7: contrato de eventos y promoción)

Base: `main@de43b6b833731c87fb6277834484545bd953d76a`. Tests no ejecutados.

## feat/commit-8b4a-promote-initial-elements
- SHA: `b91cf0a97b4a36e261243be949904c162d7b0b38`
- Último commit: test(arki): preserve immutable sufficiency fixtures (fecha desconocida) https://github.com/YvanCastilloQuezada/sicl-core/commit/b91cf0a97b4a36e261243be949904c162d7b0b38
- Comparación: behind; ahead 0, behind 35; commits exclusivos 0; rutas 0.
- Rutas: sin rutas únicas reportadas
- Lectura: Promoción de elementos iniciales; revisar compuertas y reversibilidad.
- Pruebas: no ejecutadas durante esta auditoría.
- Recomendación: verificar contrato, actor/authority, integridad y logs antes de cualquier promoción.

## feat/commit-8b4b1-d2-event-contract
- SHA: `f575dac89840c8c56c7e41efd94a3f2b46a75271`
- Último commit: 8b.4b.1: test configurable D2 commit event contract (fecha desconocida) https://github.com/YvanCastilloQuezada/sicl-core/commit/f575dac89840c8c56c7e41efd94a3f2b46a75271
- Comparación: behind; ahead 0, behind 32; commits exclusivos 0; rutas 0.
- Rutas: sin rutas únicas reportadas
- Lectura: Contrato de eventos D-2; clave para que MEMORY tenga eventos tipados y procedencia estable.
- Pruebas: no ejecutadas durante esta auditoría.
- Recomendación: verificar contrato, actor/authority, integridad y logs antes de cualquier promoción.

## feat/commit-8b4b2-developer-proposal-schemas
- SHA: `b0823ae8b87256fc7911e6bbce657f2e0b9abaca`
- Último commit: test(api): cover DeveloperProposal schema invariants (fecha desconocida) https://github.com/YvanCastilloQuezada/sicl-core/commit/b0823ae8b87256fc7911e6bbce657f2e0b9abaca
- Comparación: behind; ahead 0, behind 29; commits exclusivos 0; rutas 0.
- Rutas: sin rutas únicas reportadas
- Lectura: Esquemas de propuestas del desarrollador; separar propuesta de decisión aceptada.
- Pruebas: no ejecutadas durante esta auditoría.
- Recomendación: verificar contrato, actor/authority, integridad y logs antes de cualquier promoción.

## feat/commit-8b4b3-developer-promotion-service
- SHA: `d9027ac3f1c20569bcb1e50e20b2e6a44b551dfa`
- Último commit: test(core): cover replay after persisted effects failure (fecha desconocida) https://github.com/YvanCastilloQuezada/sicl-core/commit/d9027ac3f1c20569bcb1e50e20b2e6a44b551dfa
- Comparación: behind; ahead 0, behind 16; commits exclusivos 0; rutas 0.
- Rutas: sin rutas únicas reportadas
- Lectura: Servicio de promoción; revisar autorización y transacción.
- Pruebas: no ejecutadas durante esta auditoría.
- Recomendación: verificar contrato, actor/authority, integridad y logs antes de cualquier promoción.

## feat/commit-8b4b4-developer-promotions-endpoint
- SHA: `35888790f8bfbd0f45d99278e61ebe2c6402995a`
- Último commit: test(api): cover developer promotion endpoint contract (fecha desconocida) https://github.com/YvanCastilloQuezada/sicl-core/commit/35888790f8bfbd0f45d99278e61ebe2c6402995a
- Comparación: behind; ahead 0, behind 12; commits exclusivos 0; rutas 0.
- Rutas: sin rutas únicas reportadas
- Lectura: Endpoint de promociones; revisar autenticación, autorización y controles de mutación.
- Pruebas: no ejecutadas durante esta auditoría.
- Recomendación: verificar contrato, actor/authority, integridad y logs antes de cualquier promoción.

## feat/core-promotion-concurrency-guarantee
- SHA: `022937aecc27da956088c9b7281f745ba737d8f1`
- Último commit: fix(core): provide portable IANA timezone data (fecha desconocida) https://github.com/YvanCastilloQuezada/sicl-core/commit/022937aecc27da956088c9b7281f745ba737d8f1
- Comparación: diverged; ahead 24, behind 1; commits exclusivos 24; rutas 11.
- Rutas: api/routes/v1.py, docs/core/CORE_PROMOTION_CONCURRENCY_GUARANTEE.md, pyproject.toml, src/sicl/developer_promotion.py, src/sicl/repository.py
- Lectura: Garantía de concurrencia en promoción; verificar idempotencia y carreras.
- Pruebas: no ejecutadas durante esta auditoría.
- Recomendación: verificar contrato, actor/authority, integridad y logs antes de cualquier promoción.

## feat/dam-dna-advisor-examiner-foundation
- SHA: `f16c329bcc410cbfef1ab43a3291a5bdc58ef945`
- Último commit: fix(dam): expose drawing faculty public API (fecha desconocida) https://github.com/YvanCastilloQuezada/sicl-core/commit/f16c329bcc410cbfef1ab43a3291a5bdc58ef945
- Comparación: diverged; ahead 32, behind 1; commits exclusivos 32; rutas 17.
- Rutas: api/routes/v1.py, docs/core/CORE_PROMOTION_CONCURRENCY_GUARANTEE.md, docs/rfc/DAM-001-ADN-ASESOR-EXAMINADOR.md, pyproject.toml, src/sicl/dam/__init__.py
- Lectura: Fundación advisor/examiner DAM; delimitar rol asesor frente a evaluador y autoridad de promoción.
- Pruebas: no ejecutadas durante esta auditoría.
- Recomendación: verificar contrato, actor/authority, integridad y logs antes de cualquier promoción.

## feat/h001-examen-11-rt-a-rt-d
- SHA: `75c7cff4d9c361a663a93302c5576f8a2bff23a9`
- Último commit: fix(RFC-030): prevent synthetic IFC fixture side effects (fecha desconocida) https://github.com/YvanCastilloQuezada/sicl-core/commit/75c7cff4d9c361a663a93302c5576f8a2bff23a9
- Comparación: behind; ahead 0, behind 132; commits exclusivos 0; rutas 0.
- Rutas: sin rutas únicas reportadas
- Lectura: Examen H001 de RT-A a RT-D; conservar corpus, rúbrica y resultado exactos.
- Pruebas: no ejecutadas durante esta auditoría.
- Recomendación: verificar contrato, actor/authority, integridad y logs antes de cualquier promoción.
