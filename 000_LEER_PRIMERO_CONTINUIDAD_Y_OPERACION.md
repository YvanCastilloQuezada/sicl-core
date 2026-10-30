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
