# 000 — LEER PRIMERO: CONTINUIDAD Y OPERACIÓN DE ARKI EN EL SERVIDOR

**Propósito:** explicar dónde vive ARKI, cuál es la fuente de verdad, cómo se sincroniza con GitHub y qué debe hacerse al iniciar, trabajar, actualizar o recuperar el sistema.

**Decisión operativa:** ARKI/SICL se ejecuta en el servidor físico **Arki-02**. GitHub es el espejo remoto de código y documentación. GitHub no es el servidor de producción, no ejecuta la aplicación y no sustituye al servidor.

**Regla principal:** el servidor es el entorno operativo primario; GitHub conserva una copia versionada y permite intercambiar cambios. Ningún sincronizador puede sobrescribir cambios locales, borrar archivos sin seguimiento, forzar un push ni resolver divergencias por su cuenta.

---

## 1. Qué es lo primero que debes entender

| Elemento | Función | Autoridad |
|---|---|---|
| Servidor Arki-02 | Ejecuta SICL Core, SICL Web y los servicios de ARKI | Entorno operativo primario |
| Checkout local | Código realmente instalado y ejecutado | Estado de trabajo del servidor |
| Git local | Historial de cambios y commits del servidor | Autoridad del historial local |
| GitHub | Espejo remoto de código, documentación, PR y CI | Copia remota versionada; no runtime |
| SICL Core MEMORY | Registro canónico de eventos de continuidad | Autoridad de eventos |
| SICL Web | Interfaz, orquestación y adaptador de continuidad | No es otro Event Store |
| Mapa Vivo / reportes / handoffs | Vistas derivadas y regenerables | No son fuentes canónicas |
| ACS | Laboratorio y evidencia experimental | No sustituye Core ni AGK |

**No confundir:** que un commit esté en GitHub no significa que esté instalado en Arki-02. Que el servidor ejecute código tampoco significa que ese código ya esté guardado en GitHub.

## 2. Topología conocida del servidor

Datos registrados en revisiones previas; deben comprobarse contra el estado actual antes de instalar o modificar servicios:

- Equipo: HP Z840, nombre operativo Arki-02.
- Sistema: Ubuntu 26.04.1 LTS, x86_64.
- Usuario de operación: arki.
- Raíz de proyectos: /home/arki/ARKI.
- Core: /home/arki/ARKI/repositorios/sicl-core.
- Web: /home/arki/ARKI/repositorios/sicl-web.
- Repositorios GitHub:
  - YvanCastilloQuezada/sicl-core
  - YvanCastilloQuezada/sicl-web
  - YvanCastilloQuezada/arki-acs

En una revisión anterior existía un servicio arki02-git-sync.service que ejecutaba /home/arki/ARKI/bin/arki02-git-sync.py a las 06:30 y sincronizaba GitHub hacia Gitea. **No asumir que ese servicio sincroniza GitHub directamente con los checkouts de producción.** Antes de reutilizarlo hay que inspeccionar su código, remotos, rutas, timer y logs.

## 3. Regla de sincronización bidireccional

La sincronización es bidireccional, pero no es una fusión automática e indiscriminada.

### A. Cambios hechos en Arki-02 → GitHub

1. Comprobar qué checkout se está ejecutando y qué commit tiene.
2. Revisar git status; conservar todos los cambios modificados y no seguidos.
3. Ejecutar pruebas locales sobre ese checkout.
4. Crear un commit identificable con el resultado validado.
5. Hacer git fetch del remoto GitHub.
6. Comprobar que la rama local puede avanzar sin reescribir ni descartar historia.
7. Publicar el commit validado en GitHub.
8. Verificar que el SHA remoto coincide con el SHA local.

Un archivo modificado, una prueba fallida o un archivo no seguido bloquean la sincronización automática. No usar git reset --hard, git clean, push --force ni stash automático.

### B. Cambios hechos en GitHub → Arki-02

1. Los cambios de GitHub deben llegar por main después de revisión/CI o por el mecanismo de integración aprobado.
2. Arki-02 ejecuta git fetch; no hace pull ciego.
3. Comprobar que el checkout está limpio y que el nuevo main es descendiente del commit local.
4. Revisar el diff, instalar dependencias si corresponde y ejecutar pruebas locales.
5. Aplicar el avance con fast-forward únicamente.
6. Reiniciar solo los servicios afectados y verificar health checks.
7. Registrar el SHA instalado y el resultado de las pruebas.

Si hay divergencia, archivos locales modificados, commits sin publicar o conflictos, el proceso se detiene y genera un informe. **No hace merge automático ni elige qué versión gana.**

### C. Qué significa “espejo”

- GitHub debe reflejar los commits que ya fueron validados en Arki-02.
- Arki-02 debe incorporar los cambios aceptados en GitHub.
- La igualdad se verifica por SHA, no por el mensaje “sincronizado”.
- No se sincronizan bases de datos vivas, claves, .env, certificados privados, modelos locales ni artefactos de ejecución mediante Git.
- Los datos de MEMORY se respaldan por su mecanismo propio; GitHub no es el backup de la base de datos.

## 4. Una sola política de ramas

- main es la línea estable que se despliega en Arki-02.
- No crear ramas de prueba por rutina.
- Las ramas de PR solo se usan cuando la protección de GitHub obliga a revisar cambios antes de main.
- No fusionar ramas históricas divergentes por nombre o antigüedad.
- No desplegar un PR abierto ni una rama que no haya pasado la validación local requerida.
- Si GitHub y el servidor divergen, primero se hace auditoría de commits y archivos; nunca se fuerza la igualdad.

## 5. Comprobación inicial segura en Arki-02

Ejecutar desde una terminal del servidor. Estos comandos solo inspeccionan; no modifican ni sincronizan nada.

    hostnamectl
    whoami
    date -Is

    for repo in \
      /home/arki/ARKI/repositorios/sicl-core \
      /home/arki/ARKI/repositorios/sicl-web \
      /home/arki/ARKI/repositorios/arki-acs
    do
      echo
      echo "===== $repo ====="
      if [ -d "$repo/.git" ]; then
        git -C "$repo" status --short --branch
        git -C "$repo" remote -v
        git -C "$repo" log -1 --format='%H%n%cI%n%s'
        git -C "$repo" branch -vv
      else
        echo "CHECKOUT NO ENCONTRADO"
      fi
    done

    systemctl --user list-timers --all | grep -Ei 'arki|git|sicl|continuity' || true
    systemctl --user list-units --all | grep -Ei 'arki|git|sicl|continuity' || true

**Guardar la salida antes de cambiar remotos, ramas, timers o servicios.** Los checkouts previamente vistos tenían cambios locales y archivos sin seguimiento; no se deben limpiar sin inventario y respaldo.

## 6. Contrato del sincronizador

El sincronizador definitivo debe cumplir todos estos requisitos:

- Un único proceso activo mediante flock o bloqueo equivalente.
- Lista explícita de repositorios y rutas; no descubrir ni sincronizar carpetas arbitrarias.
- Remoto GitHub identificado y validado por URL.
- fetch primero; comparación de SHA y ancestro antes de cualquier actualización.
- Fast-forward únicamente; sin rebase automático, merge automático ni force push.
- Bloqueo ante árbol dirty, archivos untracked, divergencia, conflicto o CI fallida.
- Pruebas locales antes de publicar cambios del servidor.
- Registro JSONL con fecha, host, repo, SHA anterior, SHA nuevo, dirección, acción, resultado y motivo de bloqueo.
- Logs rotados, alertas ante bloqueo y resumen de último éxito.
- Exclusión de .env, secretos, certificados, bases de datos, cachés, dependencias y modelos pesados.
- Modo --dry-run obligatorio para el primer diagnóstico.
- Ningún servicio se reinicia si el código no pasó pruebas y health check.

**No habilitar sincronización bidireccional automática hasta verificar el sincronizador, los remotos, los checkouts y la política de conflictos en Arki-02.** Una sincronización que sobrescribe trabajo local no es continuidad: es pérdida de datos.

## 7. MEMORY: continuidad del trabajo

SICL Core es la autoridad del historial de eventos. Web captura eventos autorizados y los sincroniza hacia Core. Las proyecciones, bitácoras, roadmaps y handoffs se regeneran desde las fuentes canónicas.

Al abrir una sesión de trabajo:

1. Leer este documento.
2. Revisar estado del servidor y SHA instalados.
3. Recuperar checkpoint y eventos recientes de Core.
4. Revisar decisiones confirmadas, tareas abiertas, bloqueos, evidencias y estado FROZEN.
5. Comparar el checkout local con GitHub antes de modificar código.

Al cerrar:

1. Ejecutar pruebas y registrar exactamente cuáles se ejecutaron.
2. Guardar cambios validados en commits.
3. Sincronizar con GitHub bajo el protocolo de la sección 3.
4. Registrar pendientes, bloqueos, siguiente acción y SHA local/remoto.
5. No convertir propuestas en decisiones sin confirmación humana.

La captura automática de transcripciones completas de ChatGPT no está implementada por el mero hecho de tener esta API. Solo se registran eventos estructurados que la aplicación envía explícitamente.

## 8. Despliegue y operación

- Los servicios de Core y Web deben ejecutarse en Arki-02 mediante el gestor de servicios adoptado allí (systemd u otro ya existente).
- Los puertos, usuarios, directorios de datos, archivos Environment y comandos reales se documentan después de inspeccionar las unidades instaladas. No inventar nombres de servicios ni puertos.
- Railway y otros servicios de despliegue externos no forman parte de la arquitectura objetivo.
- GitHub Actions puede ejecutar CI y producir evidencias, pero no debe desplegar ni reemplazar el runtime local sin una decisión expresa.
- Un estado verde de CI no sustituye la prueba de ejecución en Arki-02.

## 9. Recuperación y seguridad

- Mantener copias de seguridad cifradas de la base de datos y probar restauración aislada.
- Mantener al menos una copia de seguridad independiente del servidor; un backup guardado solo en el mismo disco no protege frente a pérdida física.
- Las claves de cifrado y tokens viven fuera del repositorio, con permisos mínimos.
- No subir .env, credenciales, tokens, certificados privados, bases de datos ni backups al repositorio.
- La restauración nunca sobrescribe la base activa sin una operación explícita, respaldada y verificada.
- No modificar AGK, geometría congelada, D-2 ni estados FROZEN como parte de la sincronización.

## 10. Estado de instalación de este protocolo

Este documento define la política y los procedimientos. **No demuestra que el sincronizador bidireccional ya esté instalado ni que los servicios de Core/Web estén activos.**

Antes de activar automatización en Arki-02 deben verificarse:

- [ ] Rutas y checkouts reales de los tres repositorios.
- [ ] Remotos GitHub y cualquier remoto Gitea existente.
- [ ] Estado dirty/untracked y commits locales pendientes.
- [ ] Servicios y timers actuales, incluyendo arki02-git-sync.
- [ ] Exclusiones de secretos y datos.
- [ ] Prueba dry-run de ambas direcciones.
- [ ] Prueba de bloqueo ante divergencia y árbol dirty.
- [ ] Prueba de publicación de un commit validado.
- [ ] Prueba de incorporación fast-forward desde GitHub.
- [ ] Comparación SHA local/remoto posterior.
- [ ] Health checks de Core y Web después de actualizar.

**Criterio de aceptación:** solo declarar SERVER_GITHUB_MIRROR_VERIFIED cuando todas las pruebas anteriores estén registradas con fecha, host, repositorio, SHA y resultado.

---

**Documento de entrada:** 000_LEER_PRIMERO_CONTINUIDAD_Y_OPERACION.md  
**Autoridad operativa:** Arki-02  
**Espejo remoto:** GitHub  
**Autoridad del historial MEMORY:** SICL Core  
**Regla de integridad:** no sobrescribir, no forzar, no perder cambios; ante duda, detener y auditar.

---

## 11. Registro histórico de auditorías de repositorios y Gitea — 2026-10-30

**Fecha de corte:** 2026-10-30 (hora local de Perú, UTC-05:00).  
**Alcance:** comparación de las instancias Gitea Docker y Snap para los repositorios ARKI-ACS, SICL-Core y SICL-Web; preservación de historia Git y evaluación de metadatos.  
**Carácter:** auditorías de solo lectura, salvo la generación de informes y respaldos en directorios de auditoría. Este registro no autoriza sincronización, poda, integración, merge, push ni eliminación de referencias.

### 11.1. Inventario inicial Snap vs Docker — 2026-10-30 11:46:43

**Evidencia:** `/home/arki/ARKI/RESPALDOS/GITEA/AUDITORIA-SNAP-DOCKER-20261030-114643`

Se localizaron y validaron seis almacenes bare (tres repositorios en cada instancia), sin errores de localización o validación.

- Refs: Snap 42; Docker 241.
- ARKI-ACS: Snap 1 ref; Docker 3.
- SICL-Core: Snap 33; Docker 139.
- SICL-Web: Snap 8; Docker 99.
- La comparación inicial de commits alcanzables por todas las refs encontró historia exclusiva en ambas instancias. Estos conteos no equivalen a funcionalidades únicas ni a ramas pendientes de integración.
- Bases SQLite: Snap 118 tablas; Docker 113. Ambas devolvieron `integrity_check: ok`.
- Metadatos observados: Snap 39 releases y 31 action runs; Docker 31 releases y 23 action runs. En ambas bases se observaron 3 repositorios, 1 usuario, 0 issues y 0 PR según el inventario ejecutado.

**Lectura:** ninguna instancia podía declararse copia completa de la otra. Los objetos Git y los metadatos de Gitea debían reconciliarse por separado.

### 11.2. Verificación de respaldo Gitea — 2026-10-30 11:28:11

**Evidencia:**  
- Directorio: `/home/arki/ARKI/RESPALDOS/GITEA/GITEA-20261030-112811`
- Archivo: `/home/arki/ARKI/RESPALDOS/GITEA/GITEA-20261030-112811.tar.gz`
- SHA-256: `/home/arki/ARKI/RESPALDOS/GITEA/GITEA-20261030-112811.tar.gz.sha256`
- Log: `/home/arki/ARKI/RESPALDOS/GITEA/RESPALDO-GITEA-20261030-112811.log`

Se verificaron los checksums internos, la integridad del archivo tar y el checksum del archivo comprimido. Los archivos de base de datos estaban presentes.

**Límite de la evidencia:** esto acredita integridad del respaldo generado, no una restauración funcional. No se ha declarado un restore test satisfactorio.

### 11.3. Auditoría cruzada de almacenes — 2026-10-30 13:27:52

**Evidencia:** `/home/arki/ARKI/RESPALDOS/GITEA/AUDITORIA-CRUZADA-20261030-132752`

Los seis almacenes bare superaron `git fsck --full --strict --no-reflogs` con código de salida 0.

| Repositorio | Refs Snap | Refs Docker | Commits alcanzables Snap | Commits alcanzables Docker |
|---|---:|---:|---:|---:|
| ARKI-ACS | 1 | 3 | 90 | 90 |
| SICL-Core | 33 | 139 | 318 | 486 |
| SICL-Web | 8 | 99 | 1.868 | 2.117 |

Se identificaron referencias exclusivas en ambas instancias. Entre las referencias que requerían preservación estaban:

- ARKI-ACS Docker: `experiment/arki-ideas-acs-20261015` y `feat/oece-arki-integration-v1`.
- SICL-Core Snap: etiquetas históricas ACE85 y ACE88.
- SICL-Web Snap: etiquetas históricas AV028, AV029, AV031, AV032, AV023 y continuidad syntax.
- SICL-Core y SICL-Web Docker: referencias de trabajo relacionadas con MEMORY, AGK, F7/F8, Árbol Vivo, continuidad, DAM, IFC y otras líneas de desarrollo.

**Corrección metodológica importante:** la comprobación de ancestros debe realizarse en un almacén que contenga ambos objetos. La ausencia de un objeto remoto produce un resultado no verificable; no demuestra por sí sola que las historias sean incompatibles.

En la rama `main`, la evidencia disponible mostró que el main de Docker era ancestro del main de Snap en los tres repositorios. Snap estaba adelantado respecto a Docker:

- ARKI-ACS: Docker `1a48ed4426b958cb45be2599efc1e8d624baab80`; Snap `302f63d7c66126b248f03432fc402a4a1be6a7a6`; Snap añadía 2 commits.
- SICL-Core: Docker `588d8fa44dab7122a718e98bc1dec579c697cdbe`; Snap `934c0e56eae3c78c1f6d523d746da3e47b62ff09`; Snap añadía 12 commits.
- SICL-Web: Docker `a6d9d1bfd1962302ba1a4a41136522d6143ce694`; Snap `5c03107cda3f8c4a1d74415610fe5efa67100079`; Snap añadía 1.310 commits.

Estos resultados corresponden a las referencias y objetos examinados en esa fecha. No constituyen autorización para mover `main`.

### 11.4. Catálogo de recuperación — Macroorden 6, 2026-10-30 14:59:11

**Evidencia:** `/home/arki/ARKI/RESPALDOS/GITEA/CATALOGO-RECUPERACION-20261030-145911`

Se generó una matriz de 215 filas y un informe de 2.065 líneas:

- 53 referencias clasificadas como `EXCLUSIVA_REQUIERE_PRESERVACION`.
- 26 como `INTEGRADA_EN_MAIN_OPUESTO`.
- 132 como `INTEGRADA_EN_MAIN_PROPIO`.
- 4 como `OBJETO_EN_AMBOS_REQUIERE_REVISION`.
- 3 conflictos de nombre, correspondientes a `main`.

Las cuatro filas de objeto presente en ambas instancias representaban dos pares de referencias con el mismo SHA en SICL-Core (ACE85 y ACE88), no cuatro desarrollos independientes.

**Límite:** las categorías expresan relaciones de alcanzabilidad Git, no equivalencia funcional, vigencia ni aprobación de integración. La clasificación `INTEGRADA` no sustituye una revisión de código y pruebas.

### 11.5. Inspección de bloques y ramas — Macroorden 7, 2026-10-30

Se inspeccionaron ramas y etiquetas seleccionadas para identificar commits, archivos y alcance. Entre los resultados:

- ARKI-ACS: `experiment/arki-ideas-acs-20261015` conserva dos commits exclusivos y documentación de inventario/protocolo de recuperación.
- ARKI-ACS: `feat/oece-arki-integration-v1` no mostró commits únicos frente a main en el contraste realizado.
- SICL-Core: la etiqueta histórica ACE85 contiene cambios acotados; ACE88 contiene nueve commits, 40 archivos, 1.349 inserciones y 61 eliminaciones, incluyendo autenticación de servicio, autorización humana D2, Mapa Vivo V1, pruebas, CLI y documentación.

**Límite:** inspeccionar los cambios de una rama no acredita que sus pruebas hayan sido ejecutadas en el entorno actual ni que la funcionalidad esté desplegada.

### 11.6. Pruebas cruzadas de refs y objetos — Macroorden 8, 2026-10-30 15:27:43

**Evidencia:** `/home/arki/ARKI/RESPALDOS/GITEA/PRUEBAS-CRUZADAS-20261030-152743`

- 57 pruebas registradas.
- 535 filas de matriz.
- Cero errores reportados.
- Los seis almacenes superaron `git fsck`.
- Todas las referencias examinadas resolvieron sus objetos; cero objetos faltantes.
- Se compararon nombres de refs y SHA entre instancias.

Conteo de referencias:

| Repositorio | Mismo nombre | Mismo SHA | Mismo nombre, SHA diferente | Solo Snap | Solo Docker |
|---|---:|---:|---:|---:|---:|
| ARKI-ACS | 1 | 0 | 1 | 0 | 2 |
| SICL-Core | 31 | 30 | 1 | 2 | 108 |
| SICL-Web | 2 | 1 | 1 | 6 | 97 |

El informe inicial registró 283 comprobaciones de diferencias: 242 sin hallazgos y 41 con diagnósticos. La revisión posterior determinó que estos diagnósticos incluían hallazgos de espacios en blanco/trailing whitespace; no deben interpretarse como corrupción Git ni como fallos de integridad. Un código de salida distinto de cero en `git diff --check` puede indicar esos hallazgos.

### 11.7. Equivalencia de parches — Macroorden 9, 2026-10-30 15:31:20

**Evidencia:** `/home/arki/ARKI/RESPALDOS/GITEA/PATCH-AUDIT-20261030-153120`

Se indexaron commits alcanzables y sus patch IDs:

| Repositorio | Snap: commits / patch IDs | Docker: commits / patch IDs |
|---|---:|---:|
| ARKI-ACS | 90 / 89 | 90 / 89 |
| SICL-Core | 318 / 255 | 486 / 424 |
| SICL-Web | 1.868 / 1.770 | 2.117 / 2.050 |

Resultado global de la tabla de equivalencias: 10.684 registros:
- 10.029 registros con patch equivalente localizado en la otra instancia.
- 614 registros sin patch localizado en la otra instancia.
- 41 registros sin patch ID.

Se compararon 283 referencias mediante `git diff --check`: 242 sin hallazgos y 41 con diagnósticos.

**Interpretación y límites:**
- Los 10.029 registros no equivalen a 10.029 funcionalidades únicas: los mismos commits pueden aparecer en varias referencias.
- Los 614 registros no equivalen a 614 commits únicos.
- `patch-id` no es prueba universal de equivalencia; puede no representar adecuadamente merges, commits vacíos, cambios binarios, renombres o cambios solo de espacios.
- Un patch no localizado es candidato a preservación e inspección, no prueba automática de que falte una funcionalidad.
- Los 41 casos sin patch ID deben inspeccionarse por SHA y estructura de padres.

### 11.8. Deduplicación de commits no localizados — Macroorden 10, 2026-10-30 15:35:20

**Evidencia:** `/home/arki/ARKI/RESPALDOS/GITEA/EXCLUSIVOS-REALES-20261030-153520`

La macroorden terminó con código 0, cero errores y modo solo lectura.

| Repositorio | Origen | Commits únicos no localizados | Archivos cambiados |
|---|---|---:|---:|
| ARKI-ACS | Docker | 2 | 2 |
| SICL-Core | Docker | 174 | 359 |
| SICL-Web | Docker | 328 | 9.108 |
| SICL-Web | Snap | 9 | 24 |
| **Total** | | **513** | **9.493** |

Otros datos:
- 614 registros originales de patch no localizado.
- 513 commits únicos después de deduplicar.
- 614 asociaciones de referencias dependientes.
- 9.493 registros de archivos afectados y 8.801 rutas distintas.
- 41 commits sin patch ID.
- Cero errores.

Los principales bloques pendientes de revisión funcional son:
- SICL-Web: `feat/spatial-pilot-media-studio-v1` (196 commits), `experiment/arki-ideas-mapa-vivo-20261015` (62) y `feat/arki-operational-vitality-mo05-20261015` (44).
- SICL-Core: `docs/memory-auditoria-integracion-20261021` (69), `feat/weather-environmental-context-p1` (39), `feat/dam-dna-advisor-examiner-foundation` (32) y `feat/core-promotion-concurrency-guarantee` (26).
- ARKI-ACS: dos commits de `experiment/arki-ideas-acs-20261015`.
- SICL-Web Snap: nueve commits históricos que requieren preservación y evaluación.

Los 41 registros sin patch ID corresponden a 11 SHA distintos según el análisis de los archivos entregados. No deben descartarse ni atribuirse todos a merges: deben examinarse individualmente.

### 11.9. Conclusiones consolidadas y decisiones

1. **Integridad Git:** los seis almacenes examinados superaron las verificaciones `git fsck`; no se reportaron objetos faltantes en la auditoría cruzada.
2. **Divergencia de referencias:** Docker y Snap contienen refs y objetos exclusivos. La relación de `main` observada no elimina la necesidad de preservar ramas y etiquetas históricas.
3. **Metadatos Gitea:** las bases SQLite pasaron `integrity_check`, pero difieren en releases y action runs. La sincronización de refs Git no sincroniza usuarios, releases, ejecuciones, issues/PR ni configuración.
4. **Respaldo:** el archivo generado pasó verificaciones de integridad; falta acreditar restauración aislada.
5. **Equivalencia:** patch IDs reducen el universo de comparación, pero no prueban equivalencia funcional ni sustituyen revisión de código.
6. **Volumen pendiente:** el análisis deduplicado identificó 513 commits no localizados por patch ID, no 513 funcionalidades demostradas como faltantes.
7. **Prioridad de revisión:** SICL-Web y SICL-Core concentran el trabajo pendiente; ACS tiene un volumen menor.
8. **No poda:** ninguna rama o etiqueta debe eliminarse por estos conteos.
9. **No integración:** no se autoriza merge, cherry-pick, push, sincronización ni movimiento de `main` con base exclusiva en estas auditorías.
10. **Arquitectura:** conservar SICL Core como autoridad de eventos; SICL Web como captura/orquestación/proyección; ACS como laboratorio; AGK como única autoridad geométrica. No crear autoridades paralelas ni alterar D-2/FROZEN.

### 11.10. Próxima auditoría requerida

La siguiente etapa debe ser una auditoría funcional dirigida, de solo lectura, sobre los 513 commits y los 11 SHA sin patch ID:

- Agrupar por bloque funcional, rama, SHA y dependencias.
- Inspeccionar contenido, pruebas, contratos y evidencia de CI asociada al SHA exacto.
- Identificar cambios que afectan AGK, D-2, MEMORY, CONTINUIDAD, Árbol Vivo, DAM, IFC y Spatial Pilot.
- Clasificar cada bloque como `PRESERVAR`, `CANDIDATO_A_INTEGRAR`, `ARCHIVAR`, `OBSOLETO_POR_VERIFICAR` o `REQUIERE_REVISION`.
- Mantener separado lo declarado, implementado, ejecutado y verificado.
- No modificar refs, ramas, tags, main, servicios ni workflows.

**Criterio CERO DEUDA:** No Evidence = Not Green. Ningún bloque se declara integrado, obsoleto, recuperado o validado sin evidencia trazable.

**Estado al cierre del 2026-10-30:** `GIT_INTEGRITY_CHECKED`; `BACKUP_ARCHIVE_INTEGRITY_CHECKED`; `RESTORE_TEST_NOT_VERIFIED`; `FUNCTIONAL_EQUIVALENCE_NOT_VERIFIED`; `513_COMMITS_REQUIRE_CLASSIFICATION`; `NO_PRUNE_OR_SYNC_AUTHORIZED`.

**Nota de cronología:** las horas y fechas de los directorios de salida se conservan como identificadores de evidencia. Los informes no deben reordenarse por fecha de carga de archivos ni por fecha de modificación posterior. Cuando una fecha de commit original no fue recuperada, se mantiene como desconocida; no se inventa.

