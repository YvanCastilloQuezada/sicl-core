# SICL Core — auditoría de ramas (lote 11: mapa vivo y RFC 001–006)

Base: `main@de43b6b833731c87fb6277834484545bd953d76a`. Pruebas no ejecutadas.

## reconcile/arki-live-map-2026-10-07
- SHA: `bad480272140109e9529c3e269d525515624fc0c`
- Último commit: docs(core): establish cross-repo authority contract for F7 F8 (fecha desconocida) https://github.com/YvanCastilloQuezada/sicl-core/commit/bad480272140109e9529c3e269d525515624fc0c
- Comparación: diverged; ahead 2, behind 1; commits exclusivos 2; rutas 2.
- Rutas: docs/ARKI_CROSS_REPO_AUTHORITY_CONTRACT_V1.md, docs/ARKI_KNOWN_LIMITATIONS_v1.0.md
- Lectura: Reconciliación del mapa vivo Core; clave para contrastar eventos y estado, pero requiere comprobar si el puente es solo documental o código activo.
- Pruebas: no ejecutadas en esta auditoría.
- Recomendación: leer RFC y pruebas correspondientes; mantener separadas simulación, evidencia observada y decisión.

## rfc-001-multiscale-model
- SHA: `e4ff7423ae4d236bda956a5b0a4fd884961b99cf`
- Último commit: feat: implement canonical multiscale model scopes (fecha desconocida) https://github.com/YvanCastilloQuezada/sicl-core/commit/e4ff7423ae4d236bda956a5b0a4fd884961b99cf
- Comparación: behind; ahead 0, behind 268; commits exclusivos 0; rutas 0.
- Rutas: sin rutas únicas reportadas
- Lectura: Modelo multiescala base; contrato fundamental para entidades y relaciones espaciales.
- Pruebas: no ejecutadas en esta auditoría.
- Recomendación: leer RFC y pruebas correspondientes; mantener separadas simulación, evidencia observada y decisión.

## rfc-002-evidence-http
- SHA: `1492c07499ca438cdbda01631c6bb57b51cc3bcd`
- Último commit: feat: add canonical evidence entity and HTTP endpoints (fecha desconocida) https://github.com/YvanCastilloQuezada/sicl-core/commit/1492c07499ca438cdbda01631c6bb57b51cc3bcd
- Comparación: behind; ahead 0, behind 266; commits exclusivos 0; rutas 0.
- Rutas: sin rutas únicas reportadas
- Lectura: Contrato HTTP de evidencia; clave para referencias estables y trazabilidad.
- Pruebas: no ejecutadas en esta auditoría.
- Recomendación: leer RFC y pruebas correspondientes; mantener separadas simulación, evidencia observada y decisión.

## rfc-002-phase-c
- SHA: `700c1ae48647e8244b22c1aa71de96006c6f7405`
- Último commit: feat: implement canonical RFC-002 v1 HTTP contract (fecha desconocida) https://github.com/YvanCastilloQuezada/sicl-core/commit/700c1ae48647e8244b22c1aa71de96006c6f7405
- Comparación: behind; ahead 0, behind 268; commits exclusivos 0; rutas 0.
- Rutas: sin rutas únicas reportadas
- Lectura: Fase C del trabajo RFC-002; comparar contra contrato de evidencia y HTTP.
- Pruebas: no ejecutadas en esta auditoría.
- Recomendación: leer RFC y pruebas correspondientes; mantener separadas simulación, evidencia observada y decisión.

## rfc-003-regulatory-corpus
- SHA: `ea36d6a92b1ceaf1fdd637534e63b59b15c67a67`
- Último commit: feat: add regulatory corpus structure (fecha desconocida) https://github.com/YvanCastilloQuezada/sicl-core/commit/ea36d6a92b1ceaf1fdd637534e63b59b15c67a67
- Comparación: behind; ahead 0, behind 255; commits exclusivos 0; rutas 0.
- Rutas: sin rutas únicas reportadas
- Lectura: Corpus regulatorio; conservar jurisdicción, versión y procedencia normativa.
- Pruebas: no ejecutadas en esta auditoría.
- Recomendación: leer RFC y pruebas correspondientes; mantener separadas simulación, evidencia observada y decisión.

## rfc-004-design-intelligence-scope
- SHA: `8bdf1b1367cd375873bf7225b95e0116b2069bcc`
- Último commit: feat: add read-only design intelligence catalog (fecha desconocida) https://github.com/YvanCastilloQuezada/sicl-core/commit/8bdf1b1367cd375873bf7225b95e0116b2069bcc
- Comparación: behind; ahead 0, behind 261; commits exclusivos 0; rutas 0.
- Rutas: sin rutas únicas reportadas
- Lectura: Alcance de inteligencia de diseño; frontera entre recomendación y decisión.
- Pruebas: no ejecutadas en esta auditoría.
- Recomendación: leer RFC y pruebas correspondientes; mantener separadas simulación, evidencia observada y decisión.

## rfc-005-evaluation-comparison-http
- SHA: `ad59f89bf0f27b0597ee60f62048adc9bcaf8c3f`
- Último commit: feat: expose evaluation and comparison over HTTP v1 (fecha desconocida) https://github.com/YvanCastilloQuezada/sicl-core/commit/ad59f89bf0f27b0597ee60f62048adc9bcaf8c3f
- Comparación: behind; ahead 0, behind 265; commits exclusivos 0; rutas 0.
- Rutas: sin rutas únicas reportadas
- Lectura: Evaluación/comparación HTTP; revisar métricas y consistencia de resultados.
- Pruebas: no ejecutadas en esta auditoría.
- Recomendación: leer RFC y pruebas correspondientes; mantener separadas simulación, evidencia observada y decisión.

## rfc-006-1-monte-carlo
- SHA: `01ce186bd8835eedde90a3ec316ec21819ee24b2`
- Último commit: feat: implement RFC-006.1 Monte Carlo simulation (fecha desconocida) https://github.com/YvanCastilloQuezada/sicl-core/commit/01ce186bd8835eedde90a3ec316ec21819ee24b2
- Comparación: diverged; ahead 1, behind 240; commits exclusivos 1; rutas 7.
- Rutas: api/routes/v1.py, docs/RFC-006.1_MONTE_CARLO.md, docs/RFC-006_SIMULATION_CONTRACT.md, docs/SICL_CORE_CONTRACT_v1.0.md, src/sicl/cli.py
- Lectura: Monte Carlo; la simulación debe etiquetarse SIMULATED y no como observado/FACT.
- Pruebas: no ejecutadas en esta auditoría.
- Recomendación: leer RFC y pruebas correspondientes; mantener separadas simulación, evidencia observada y decisión.
