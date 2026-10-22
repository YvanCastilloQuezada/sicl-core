# SICL Core — auditoría de ramas (lote 6: persistencia, validación y promoción)

Base: `main@de43b6b833731c87fb6277834484545bd953d76a`. No se ejecutaron pruebas.

## feat/arkidraw-block2-scene-adapter
- SHA: `c13c0eac896ac4b6adde80646f30e9b96dccee51`
- Último commit: fix(arkidraw): enforce semantic role gate (fecha desconocida) https://github.com/YvanCastilloQuezada/sicl-core/commit/c13c0eac896ac4b6adde80646f30e9b96dccee51
- Comparación: diverged; ahead 2, behind 89; commits exclusivos 2; rutas 4.
- Rutas: docs/architecture/ARKI_DRAW_BLOCK2_REALITY_AUDIT.md, src/sicl/drawing/__init__.py, src/sicl/drawing/scene_adapter.py, tests/test_drawing_block2.py
- Lectura: Adaptador de escena para ARKIDraw bloque 2; comprobar continuidad con bloque 1.
- Pruebas: no ejecutadas durante esta auditoría.
- Recomendación: estas ramas son una secuencia de commits/etapas; evaluar el orden de dependencia y evitar integrar etapas duplicadas o superadas.

## feat/commit-8a-d2-persistence
- SHA: `2e57db08e96a86e97ddd5581b1df379e1bdc8068`
- Último commit: test(api): cover read-only D-2 endpoints (fecha desconocida) https://github.com/YvanCastilloQuezada/sicl-core/commit/2e57db08e96a86e97ddd5581b1df379e1bdc8068
- Comparación: behind; ahead 0, behind 75; commits exclusivos 0; rutas 0.
- Rutas: sin rutas únicas reportadas
- Lectura: Persistencia D-2; verificar transacciones y autoridad del repositorio.
- Pruebas: no ejecutadas durante esta auditoría.
- Recomendación: estas ramas son una secuencia de commits/etapas; evaluar el orden de dependencia y evitar integrar etapas duplicadas o superadas.

## feat/commit-8b1-human-review-binding
- SHA: `0c7d04d52582d7d12b9a3c116abf9caac1ec16f7`
- Último commit: fix(review): map proposal fingerprint mismatch to conflict (fecha desconocida) https://github.com/YvanCastilloQuezada/sicl-core/commit/0c7d04d52582d7d12b9a3c116abf9caac1ec16f7
- Comparación: behind; ahead 0, behind 67; commits exclusivos 0; rutas 0.
- Rutas: sin rutas únicas reportadas
- Lectura: Vinculación de revisión humana; es relevante para impedir promoción sin actor/authority.
- Pruebas: no ejecutadas durante esta auditoría.
- Recomendación: estas ramas son una secuencia de commits/etapas; evaluar el orden de dependencia y evitar integrar etapas duplicadas o superadas.

## feat/commit-8b2-fix-publication-duplication
- SHA: `c5044b54588a43421f2eaffbfc2330d94de83262`
- Último commit: test(arki): enforce single publication invocation (fecha desconocida) https://github.com/YvanCastilloQuezada/sicl-core/commit/c5044b54588a43421f2eaffbfc2330d94de83262
- Comparación: behind; ahead 0, behind 58; commits exclusivos 0; rutas 0.
- Rutas: sin rutas únicas reportadas
- Lectura: Corrección de duplicación de publicación; inspeccionar idempotencia y posibles pérdidas.
- Pruebas: no ejecutadas durante esta auditoría.
- Recomendación: estas ramas son una secuencia de commits/etapas; evaluar el orden de dependencia y evitar integrar etapas duplicadas o superadas.

## feat/commit-8b2-publication-refactor
- SHA: `389806ec6f656e840ad28c9d7c015f026b715aac`
- Último commit: test(archi): import publication result explicitly (fecha desconocida) https://github.com/YvanCastilloQuezada/sicl-core/commit/389806ec6f656e840ad28c9d7c015f026b715aac
- Comparación: behind; ahead 0, behind 61; commits exclusivos 0; rutas 0.
- Rutas: sin rutas únicas reportadas
- Lectura: Refactor de publicación; comparar con rama de corrección de duplicación y decidir qué variante contiene la solución final.
- Pruebas: no ejecutadas durante esta auditoría.
- Recomendación: estas ramas son una secuencia de commits/etapas; evaluar el orden de dependencia y evitar integrar etapas duplicadas o superadas.

## feat/commit-8b3a-creation-validation
- SHA: `e4ddcde4d475ab86bf4e54b4b5736348a837b9c8`
- Último commit: test(archi): cover structural creation validation (fecha desconocida) https://github.com/YvanCastilloQuezada/sicl-core/commit/e4ddcde4d475ab86bf4e54b4b5736348a837b9c8
- Comparación: behind; ahead 0, behind 58; commits exclusivos 0; rutas 0.
- Rutas: sin rutas únicas reportadas
- Lectura: Validación de creación; verificar errores y reglas de esquema.
- Pruebas: no ejecutadas durante esta auditoría.
- Recomendación: estas ramas son una secuencia de commits/etapas; evaluar el orden de dependencia y evitar integrar etapas duplicadas o superadas.

## feat/commit-8b3a-ri-referential-integrity
- SHA: `34e7c7d3f15f5f268a23d28c33471508cf0c61d2`
- Último commit: test(arki): fail closed on orphan IFC references (fecha desconocida) https://github.com/YvanCastilloQuezada/sicl-core/commit/34e7c7d3f15f5f268a23d28c33471508cf0c61d2
- Comparación: behind; ahead 0, behind 45; commits exclusivos 0; rutas 0.
- Rutas: sin rutas únicas reportadas
- Lectura: Integridad referencial; importante para decisiones/evidencias enlazadas.
- Pruebas: no ejecutadas durante esta auditoría.
- Recomendación: estas ramas son una secuencia de commits/etapas; evaluar el orden de dependencia y evitar integrar etapas duplicadas o superadas.

## feat/commit-8b3b-a002-creation-adapter
- SHA: `f1ffeb9ad236df39be02dc164c1e867aafa67d80`
- Último commit: fix(arki): import SpatialScope from its defining module (fecha desconocida) https://github.com/YvanCastilloQuezada/sicl-core/commit/f1ffeb9ad236df39be02dc164c1e867aafa67d80
- Comparación: behind; ahead 0, behind 39; commits exclusivos 0; rutas 0.
- Rutas: sin rutas únicas reportadas
- Lectura: Adaptador de creación A-002; comprobar que no eluda validaciones del dominio.
- Pruebas: no ejecutadas durante esta auditoría.
- Recomendación: estas ramas son una secuencia de commits/etapas; evaluar el orden de dependencia y evitar integrar etapas duplicadas o superadas.
