# ARKI — Mapa Vivo V1

Estado: **IMPLEMENTED (read-only graph generator) / RUNTIME ON ARKI-02 NOT YET VALIDATED / NOT FROZEN**.

## Ejecución en ARKI-02

```bash
cd /home/arki/ARKI/repositorios/sicl-core
git pull --ff-only
python3 tools/arki_mapa_vivo.py --root . --output "$HOME/Descargas/ARKI_MAPA_VIVO.json"
```

El generador emite JSON de nodos, aristas, dependencias, evidencia de archivos con SHA-256 y hallazgos. Solo escribe en la ruta de salida indicada, que debe estar fuera del repositorio. No modifica SQLite ni ejecuta promoción ACE88.

## Lectura correcta

- F1–F10: `UNKNOWN` hasta obtener pruebas por fase; las precedencias secuenciales son provisionales, no la ruta crítica definitiva.
- `SOURCE_PRESENT_NOT_VALIDATED`: archivo presente, no capacidad demostrada.
- `MISSING`: evidencia fuente ausente.
- `approval` se mantiene separado de `status`.
- Los colores son señales de incertidumbre visual, no madurez certificada.
- Las relaciones canónicas, actividades secundarias, FROZEN, árbol gemelo, alternativas y propagación incremental requieren ingesta verificada de contratos reales.

## Próximo hito

1. Ejecutar el generador en ARKI-02 y verificar JSON.
2. Ingerir contratos reales F1–F10, dependencias, evidencias y FROZEN, sin inferencias.
3. Incorporar detector de ciclos, huérfanos, propagación de bloqueos y prioridades primogénitas.
4. Añadir vista interactiva del mapa, con selección de fase y panel de espinas.
5. Conectar el ciclo de tres alternativas en sandbox, aprobación ACE88 y reevaluación.
6. Actualizar `00-start.md` con SHA, evidencias y limitaciones después de cada hito.
