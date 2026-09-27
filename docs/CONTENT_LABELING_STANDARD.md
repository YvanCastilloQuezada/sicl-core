# ARKI Content Labeling Standard

## 1. Propósito

ARKI etiqueta explícitamente el contenido generado por IA para cumplir con obligaciones de transparencia como el Art. 50 del EU AI Act.

## 2. Estándar técnico

El esquema de metadatos de proveniencia está delimitado a un hash de integridad SHA-256; no implementa una firma C2PA, RSA ni autenticidad criptográfica.

## 3. Requisitos del output

Todo output generado debe incluir `provenance_hash`, conforme a la Regla 42, con identificador del generador, timestamp, hash SHA-256, referencia de dominio y fuentes.

## 4. Consecuencias del incumplimiento

Contenido sin sello, con hash ausente o con hash discrepante se considera `UNVERIFIED` o `TAMPERED` y no debe promoverse a `CANONICAL`.

**Versión:** 1.0 | **Fecha:** 2026-09-28 | **Estado:** EXPERIMENTAL
