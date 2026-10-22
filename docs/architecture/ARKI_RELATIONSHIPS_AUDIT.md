# ARKI — Auditoría de Relaciones Arquitectónicas

Fecha: 2026-09-29  
HEAD auditado: `9543518e87a826df8d41de45c0e1dc1355f3d9ab`  
Modo: READ-ONLY sobre producción; sin cambios de código

## 1. Inventario real

- `RelationshipKind = {HOSTED_IN, BOUNDS}`.
- `ArchiRelationship`: dirigida, versiona extremos, ID determinista, prohíbe autorreferencia.
- `HOSTED_IN` = hijo → host.
- `BOUNDS`: enum sin test que demuestre su semántica arquitectónica.
- `contained_in` existe en `ArchiElement`, pero no hay `RelationshipKind.CONTAINED_IN`.
- No hay test que demuestre `BOUNDS == contained_in`.

## 2. Separación con H-001

Confirmada y testeada:
- `architectural_derivation()` documenta que `HOSTED_IN/BOUNDS` quedan fuera.
- `test_archi_relationships.py` exige que `HOSTED_IN` no entre a `TypedRelation`.

## 3. Persistencia

- `relationships.py` no importa `Event` ni `now_iso`.
- No escribe al Event Store.
- `ArchiTransaction` mantiene `tuple[ArchiElement, ...]` como canonical.
- `ArchiRelationship` no está incorporado al estado canónico transaccional.

## 4. Gap demostrado

`ArchiRelationship` existe como contrato arquitectónico, pero no está
demostrado que forme parte persistente del estado D-2 ni que sea la
fuente de verdad de `hosted_in/contained_in`.

Tres representaciones parcialmente desconectadas:
- `ArchiElement.hosted_in / contained_in → semantic_dict → content_hash`
- `ArchiRelationship {HOSTED_IN, BOUNDS}` → sin persistencia Event Store,
  sin integración ArchiTransaction
- `DerivationLedger.TypedRelation` → causal, no espacial

Riesgo: `ArchiElement.hosted_in` y `ArchiRelationship(kind=HOSTED_IN)`
pueden divergir sin fuente única de verdad.

## 5. Decisiones

- NO autorizar ampliación de `RelationshipKind` sin gap demostrado.
- NO tocar `derivation.py`: la separación H-001 / relaciones arquitectónicas está bien codificada y testeada.
- NO crear segundo estado canónico para relaciones.
- La red arquitectónica debe vivir DENTRO del único D-2.

## 6. Próximo commit específico

Definir cómo `ArchiRelationship` se integra al estado canónico D-2
sin duplicar `hosted_in/contained_in` ni crear estado paralelo.

Requiere decisión de diseño específica, no resoluble por auditoría.

Sin cambios de código de producción.
