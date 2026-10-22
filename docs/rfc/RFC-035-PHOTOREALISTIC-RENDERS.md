# RFC-035 — Photorealistic Renders

**Estado:** STUB — FUTURE
**Prioridad:** Baja, posterior a RFC-034
**Dependencias:** RFC-027, RFC-030, RFC-034
**Namespace CLI:** `/RENDER`
**Namespace HTTP:** `/renders`

## 1. Resumen

RFC-035 definirá el modo de generación de renders fotorrealistas para comunicación visual de alta calidad: marketing, portafolio y presentaciones premium.

## 2. Fixture de referencia

```text
docs/reference/RFC-035/
├── torres_exterior.png   (Torres Doble Hélice, exterior al atardecer)
└── torres_interior.png   (Torres Doble Hélice, interior con doble altura)
```

## 3. Alcance preliminar

- Generación desde `BIMModelSnapshot`.
- Iluminación realista: hora dorada, atardecer y nocturna.
- Materiales PBR.
- Contexto paisajístico.
- Cámara configurable.
- Salidas 2K y 4K.
- Exportación PNG/JPG.

## 4. Fuera de alcance

- No es plano técnico: RFC-030.
- No es lámina de presentación: RFC-034.
- No es video ni animación.

## 5. Estado

Este RFC se implementará después de RFC-034. Por ahora solo fija el namespace, el fixture esperado y el alcance preliminar. No se implementa código en RFC-035 mediante este documento.
