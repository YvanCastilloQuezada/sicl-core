# Auditoría de coherencia RFC-015–026

**Fecha:** 16 de septiembre de 2026

## Resultado ejecutivo

La implementación actual está más avanzada que varios encabezados documentales. Las simulaciones, el filtro de factibilidad, las variables por escala, el conocimiento de diseño y el corpus normativo están implementados en distintos niveles. El principal riesgo documental era mezclar el histórico de ramas con el estado de `main`.

## Correcciones aplicadas

Se actualizaron los manuales, el contrato y la arquitectura para registrar el catálogo real de simulaciones, las distribuciones Monte Carlo, el filtro `feasible_pareto_front`, los cuatro métodos de generación, la separación `GeneratedAlternative`/`Alternative`, el estado de `llm_assisted_v1`, las variables por escala, los ciclos temporales, el piloto RNE y el agente de conocimiento.

También se documentó la colisión nominal entre dos iniciativas llamadas RFC-019. En el Core, RFC-019 significa refinamiento multiescala. En el frontend, RFC-019 significa alias localizados. Son trabajos distintos y no deben compartir estado ni aprobación.

## Hallazgos por grupo

| Grupo | Hallazgo | Resolución |
|---|---|---|
| RFC-015–016 | Capacidades funcionales presentes, pero los manuales no destacaban Source HTTP y el alcance real del frontend | Añadidas referencias y matriz vigente |
| RFC-017–018 | Documentos conservaban `DRAFT` y ramas históricas pese a estar fusionados | El estado vigente se registra como política/documentación activa en main; se conserva el encabezado histórico |
| RFC-019 Core | Documento decía “en la rama” | La arquitectura vigente lo identifica como implementado en main |
| RFC-019 Frontend | Alias localizados mezclados nominalmente con el RFC Core | Se separan explícitamente como RFC-019 Frontend |
| RFC-020–021 | Implementación presente, pero simulaciones y variables no estaban resumidas en la arquitectura actual | Añadida matriz y sección técnica |
| RFC-022 | Guided Interface implementada; documentación previa describía menos módulos que el menú | Se documenta el Camino A y módulos complementarios |
| RFC-023–024 | Conectividad local/mock verificada; remoto bloqueado | Se mantiene el bloqueo, sin declarar E2E remoto |
| RFC-025 | Piloto normativo ampliado y revisión E.030 no reflejados en una matriz general | Añadidos corpus, estados y revisión humana |
| RFC-026 | Piloto funcional y endpoints presentes, pero persistencia bibliográfica completa aún es plan | Se distingue piloto implementado de fase bibliográfica pendiente |

## Verificaciones ejecutadas

- Core: 241 pruebas pasando.
- Frontend: 126 pruebas pasando.
- Typecheck frontend: PASS.
- Build frontend: PASS.
- `compileall`: PASS.
- `git diff --check`: PASS.

## Estado que no debe declararse todavía

No debe declararse E2E remoto, Ollama productivo, add-in nativo de Revit, plugin nativo de Archicad ni corpus bibliográfico masivo como capacidades verificadas.

## References

[1]: https://github.com/YvanCastilloQuezada/sicl-core "SICL Core repository"
[2]: https://github.com/YvanCastilloQuezada/sicl-web "SiMS-DeI web repository"
