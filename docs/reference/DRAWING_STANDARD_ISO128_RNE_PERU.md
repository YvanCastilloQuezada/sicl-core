# Drawing Standard — ISO 128 + RNE Perú

**Rule set:** `ISO128_RNE_PERU`
**Archivo normativo:** `data/drawing_rules/iso128_rne_peru.json`
**Namespace:** `/DRAWING`
**Estado:** Implementado en RFC-030

## Alcance

Este estándar define la representación gráfica de los planos técnicos generados por ARKI. Codifica pesos de línea, achurados, simbología arquitectónica, cotas y niveles para que el proyector y el exportador trabajen con un contrato común.

## Reglas principales

| Elemento | Regla |
|---|---|
| Línea de construcción | 0.18 mm |
| Línea secundaria | 0.35 mm |
| Elemento cortado | 0.50 mm |
| Perfil principal | 0.70 mm |
| Muro de concreto | 0.20 m + achurado diagonal 30 % |
| Muro de albañilería | 0.15 m + achurado diagonal 50 % |
| Tabique | 0.10 m + achurado diagonal 70 % |
| Puerta | Arco de 90° + hoja + eje de apertura |
| Ventana | Dos líneas paralelas + marco + alféizar |
| Escalera | Peldaños + flecha de dirección; 14 peldaños en el fixture |
| Cotas | Dos anillos: parciales/entre ejes y totales |
| Nivel NPT | Símbolo triangular + etiqueta numérica |
| Ejes | Círculo de 8 mm con letra o número |

## Separación de namespaces

- RFC-030 / `/DRAWING`: planos técnicos y salidas A3.
- RFC-034 / `/PRESENTATION`: láminas de presentación.
- RFC-036 / `/CONCEPTUAL`: anteproyectos conceptuales.

El `DrawingRuleSet` no modifica el BIM snapshot, no crea decisiones y no cambia el Core determinista.

## Validación

El test `test_plan_matches_drawing_standard` comprueba que una planta generada contiene muros con espesor, escalera con flecha, cotas numéricas y niveles NPT triangulares. La suite RFC-030 mantiene además las pruebas de diferenciación de planta, cortes, elevación y cubierta.

> Las salidas siguen siendo representaciones técnicas generadas para revisión. La documentación municipal y la construcción requieren validación y firma profesional.
