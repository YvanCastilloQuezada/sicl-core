# SICL Core — auditoría de ramas (lote 2: arquitectura y Mapas Vivos P0)

Base: `main@de43b6b833731c87fb6277834484545bd953d76a`. No se ejecutaron pruebas.

## docs/master-architecture-v2
- SHA: `14e31987cff90f4cc93a7167e2d28c5f5cb8be9f`
- Último commit: docs: add SiMS-DeI 2.0 master architecture (fecha desconocida) https://github.com/YvanCastilloQuezada/sicl-core/commit/14e31987cff90f4cc93a7167e2d28c5f5cb8be9f
- Comparación: behind; ahead 0, behind 251; commits exclusivos 0; rutas 0.
- Rutas: sin rutas únicas reportadas
- Lectura: Versión de arquitectura maestra; v2 y v2.2 deben compararse semánticamente y no solo por número de versión.
- Pruebas: no ejecutadas.
- Recomendación: comparar con main y el conjunto de esquemas antes de integrar; no asumir que documentos en ramas ya están vigentes.

## docs/master-architecture-v2.2
- SHA: `c83d6ed3028092603b681fc1ad0ed1105fe67d8a`
- Último commit: docs: add SiMS-DeI 2.2 master architecture (fecha desconocida) https://github.com/YvanCastilloQuezada/sicl-core/commit/c83d6ed3028092603b681fc1ad0ed1105fe67d8a
- Comparación: behind; ahead 0, behind 225; commits exclusivos 0; rutas 0.
- Rutas: sin rutas únicas reportadas
- Lectura: Versión de arquitectura maestra; v2 y v2.2 deben compararse semánticamente y no solo por número de versión.
- Pruebas: no ejecutadas.
- Recomendación: comparar con main y el conjunto de esquemas antes de integrar; no asumir que documentos en ramas ya están vigentes.

## docs/master-frozen-future-orders
- SHA: `de949f5cc3773d18cdedfb4b9cf19d0749d3315a`
- Último commit: docs: consolidate SiMS-DeI frozen future orders (fecha desconocida) https://github.com/YvanCastilloQuezada/sicl-core/commit/de949f5cc3773d18cdedfb4b9cf19d0749d3315a
- Comparación: diverged; ahead 1, behind 184; commits exclusivos 1; rutas 1.
- Rutas: docs/future/SiMS_DeI_MASTER_FROZEN_FUTURE_ORDERS.md
- Lectura: Matriz de órdenes FROZEN/FUTURE; conservar autoridad, procedencia y estados.
- Pruebas: no ejecutadas.
- Recomendación: comparar con main y el conjunto de esquemas antes de integrar; no asumir que documentos en ramas ya están vigentes.

## docs/mv-p0-1-common-variable-schema
- SHA: `c7d9cdee2aaa6a8ee7ccabc304515bc8a444336d`
- Último commit: docs: specify common multiscale variable schema (fecha desconocida) https://github.com/YvanCastilloQuezada/sicl-core/commit/c7d9cdee2aaa6a8ee7ccabc304515bc8a444336d
- Comparación: diverged; ahead 2, behind 184; commits exclusivos 2; rutas 2.
- Rutas: docs/architecture/MV_P0_0_CURRENT_VARIABLE_ARCHITECTURE_AUDIT.md, docs/architecture/MV_P0_1_COMMON_MULTISCALE_VARIABLE_SCHEMA.md
- Lectura: Esquema común de variables para Mapas Vivos P0-1; verificar estabilidad/versionado del contrato.
- Pruebas: no ejecutadas.
- Recomendación: comparar con main y el conjunto de esquemas antes de integrar; no asumir que documentos en ramas ya están vigentes.

## docs/mv-p0-2-object-variable-matrix
- SHA: `2c3d8e20a39eede18399d955d7437e60fc6e7b80`
- Último commit: docs: define object-scale variable matrix (fecha desconocida) https://github.com/YvanCastilloQuezada/sicl-core/commit/2c3d8e20a39eede18399d955d7437e60fc6e7b80
- Comparación: diverged; ahead 3, behind 184; commits exclusivos 3; rutas 3.
- Rutas: docs/architecture/MV_P0_0_CURRENT_VARIABLE_ARCHITECTURE_AUDIT.md, docs/architecture/MV_P0_1_COMMON_MULTISCALE_VARIABLE_SCHEMA.md, docs/architecture/MV_P0_2_OBJECT_VARIABLE_MATRIX.md
- Lectura: Matriz de variables de objeto P0-2; comprobar vocabulario y herencia multiescala.
- Pruebas: no ejecutadas.
- Recomendación: comparar con main y el conjunto de esquemas antes de integrar; no asumir que documentos en ramas ya están vigentes.

## docs/mv-p0-3-space-variable-matrix
- SHA: `3789fdd6464556637dc54f6602e3550a354b6483`
- Último commit: docs: define space-scale variable matrix (fecha desconocida) https://github.com/YvanCastilloQuezada/sicl-core/commit/3789fdd6464556637dc54f6602e3550a354b6483
- Comparación: diverged; ahead 4, behind 184; commits exclusivos 4; rutas 4.
- Rutas: docs/architecture/MV_P0_0_CURRENT_VARIABLE_ARCHITECTURE_AUDIT.md, docs/architecture/MV_P0_1_COMMON_MULTISCALE_VARIABLE_SCHEMA.md, docs/architecture/MV_P0_2_OBJECT_VARIABLE_MATRIX.md, docs/architecture/MV_P0_3_SPACE_VARIABLE_MATRIX.md
- Lectura: Matriz de variables de espacio P0-3; revisar compatibilidad con esquema común.
- Pruebas: no ejecutadas.
- Recomendación: comparar con main y el conjunto de esquemas antes de integrar; no asumir que documentos en ramas ya están vigentes.

## docs/mv-p0-13-cross-scale-canonicalization
- SHA: `be2aa8733a1ac5eecc439859a989aae25543d6cb`
- Último commit: docs: canonicalize cross-scale variable semantics (fecha desconocida) https://github.com/YvanCastilloQuezada/sicl-core/commit/be2aa8733a1ac5eecc439859a989aae25543d6cb
- Comparación: diverged; ahead 7, behind 184; commits exclusivos 7; rutas 17.
- Rutas: docs/architecture/MV_P0_0_CURRENT_VARIABLE_ARCHITECTURE_AUDIT.md, docs/architecture/MV_P0_10_REGION_VARIABLE_MATRIX.md, docs/architecture/MV_P0_11_MACRO_REGION_VARIABLE_MATRIX.md, docs/architecture/MV_P0_12_COUNTRY_VARIABLE_MATRIX.md, docs/architecture/MV_P0_13_CANONICAL_VARIABLE_REGISTER.md, docs/architecture/MV_P0_13_CROSS_SCALE_SEMANTIC_CANONICALIZATION.md
- Lectura: Canonicalización entre escalas; revisar invariantes para evitar dos representaciones canónicas.
- Pruebas: no ejecutadas.
- Recomendación: comparar con main y el conjunto de esquemas antes de integrar; no asumir que documentos en ramas ya están vigentes.

## docs/mv-p0-batch-a2-system-building-site
- SHA: `c20433ea83dec156b1338ea2756d76c9d1dbd8e6`
- Último commit: docs: define system building and site variable matrices (fecha desconocida) https://github.com/YvanCastilloQuezada/sicl-core/commit/c20433ea83dec156b1338ea2756d76c9d1dbd8e6
- Comparación: diverged; ahead 5, behind 184; commits exclusivos 5; rutas 8.
- Rutas: docs/architecture/MV_P0_0_CURRENT_VARIABLE_ARCHITECTURE_AUDIT.md, docs/architecture/MV_P0_1_COMMON_MULTISCALE_VARIABLE_SCHEMA.md, docs/architecture/MV_P0_2_OBJECT_VARIABLE_MATRIX.md, docs/architecture/MV_P0_3_SPACE_VARIABLE_MATRIX.md, docs/architecture/MV_P0_4_SYSTEM_VARIABLE_MATRIX.md, docs/architecture/MV_P0_5_BUILDING_VARIABLE_MATRIX.md
- Lectura: Lote A2 de edificios/sitio; confirmar dependencias y si los datos son contractuales o ilustrativos.
- Pruebas: no ejecutadas.
- Recomendación: comparar con main y el conjunto de esquemas antes de integrar; no asumir que documentos en ramas ya están vigentes.
