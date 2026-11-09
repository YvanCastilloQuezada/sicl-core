# 00_HANDOFF_INICIO_ARKI

**Fecha:** 2026-11-05  
**Proyecto:** ARKI / SICL-Web  
**Propósito:** Continuidad técnica de la migración MySQL → SQLite.

> Este documento registra el estado confirmado en el handoff y los logs compartidos. No afirma que SQLite esté integrado ni que los datos hayan sido migrados.

## 1. Estado de la migración

- Rama local reportada: `migration/sicl-web-sqlite-20261103-013118`
- HEAD reportado: `4404c3ccfd7c5beeeb951661942ebccd807d9610`
- Commit: `fix(sqlite): enforce globally unique project IDs`
- Backend vigente según auditoría: MySQL mediante `server/db.ts` y `DATABASE_URL`.
- SQLite permanece aislado; no es todavía el backend operativo de los routers y servicios.

## 2. Auditorías previas

### MO133 — Repositorios SQLite
Se reportaron cinco repositorios SQLite:
- usuarios
- proyectos
- archivos paramétricos
- sesiones ARKI
- handoffs

Todos usan `openSiclSqlite()` desde `server/db.sqlite.adapter.ts`. MO133 no ejecutó migraciones ni modificó datos.

### MO134 — Compatibilidad de contratos
Hallazgos reportados:
- Los repositorios SQLite tienen factories, nombres y firmas que no coinciden necesariamente con las funciones públicas de MySQL.
- Routers y servicios continúan usando `server/db.ts`.
- El esquema SQLite tiene diferencias de tipos, timestamps y restricciones.
- La inspección de dependencias quedó incompleta por un error de sintaxis en el comando Node.
- No se debe reemplazar mecánicamente el backend antes de adaptar y validar el contrato.

### MO135 — Inventario de bases
MO135 fue planteado como inspección de solo lectura de MySQL, SQLite, tablas, columnas, conteos, índices, relaciones y configuración. El log completo no estaba disponible en el contexto revisado. Por tanto, el inventario real y la migración de datos siguen **pendientes de evidencia**.

## 3. Preservación y riesgos

- Se reportó un respaldo verificado en:
  `/home/arki/ARKI-COMMIT-BACKUP-20261105-011638/sicl-web-migration_sicl-web-sqlite-20261103-013118.tar.gz`
- En la rama se reportaron archivos no rastreados: `data/`, `drizzle/sqlite/`, `server/parametric/`, pruebas y numerosos backups MO.
- No incluir indiscriminadamente esos archivos en un commit.
- No borrar bases, WAL/SHM, respaldos ni datos existentes sin verificación y autorización explícita.
- El respaldo reportado contiene el árbol de trabajo; no equivale por sí solo a demostrar que la migración de datos fue validada.

## 4. Objetivo y secuencia de trabajo

Objetivo: migrar los datos y el runtime de MySQL a SQLite sin pérdida ni ruptura funcional.

1. Recuperar el log completo MO135 y completar el inventario de MySQL y SQLite.
2. Verificar respaldo, integridad y posibilidad de restauración.
3. Definir mapeo de tablas, tipos, IDs, timestamps, índices, restricciones y relaciones.
4. Migrar datos a SQLite preservando identidad y relaciones; no sobrescribir el destino sin comparar.
5. Implementar una capa de compatibilidad que conserve el contrato público usado por routers y servicios.
6. Ejecutar pruebas de autenticación, CRUD, sesiones, archivos paramétricos y handoffs.
7. Comparar conteos y validar integridad referencial y casos límite.
8. Cambiar el runtime a SQLite solo después de superar las verificaciones.
9. Retirar MySQL del runtime únicamente tras aceptación documentada.

## 5. Criterios de cierre

La migración no se considera completa hasta que:
- existe inventario reproducible de origen y destino;
- respaldo y restauración están comprobados;
- conteos y relaciones están conciliados;
- los routers y servicios usan SQLite mediante contrato compatible;
- pruebas relevantes pasan;
- el runtime inicia y opera con SQLite;
- el resultado y evidencias quedan registrados.

## 6. Estado de acciones

Según los registros compartidos:
- No se confirmó migración de datos.
- No se confirmó sustitución de MySQL en `server/db.ts`.
- No se confirmó commit/push/merge de esta documentación.
- La rama tenía un conjunto significativo de archivos no rastreados y backups.
- No se deben crear ramas de prueba adicionales para continuar esta tarea.

## 7. Próximo paso

Obtener el log íntegro `sicl-web-mo135-20261104-215559.log` (o el log MO135 real más reciente), revisar `00_start.md` del repositorio y actualizar este handoff con evidencia concreta. Después, ejecutar una prueba de lectura del documento y comprobar su integridad antes de incorporarlo al repositorio canónico.

---
**Regla de evidencia:** no marcar una etapa como terminada por existir código o una base SQLite. Debe haber prueba de ejecución y verificación de datos.


## 8. Arranque y validación de SICL-Web — MO47

### 8.1 Identidad de la ejecución confirmada

Log recibido: `sicl-web-sqlite-mo47-20261105-021309.log`

- Fecha: `2026-11-05T02:13:09-05:00`
- Repositorio: `/home/arki/ARKI/canonical/sicl-web`
- Rama: `migration/sicl-web-sqlite-20261103-013118`
- HEAD: `4404c3ccfd7c5beeeb951661942ebccd807d9610`

### 8.2 Comando de ejecución MO47

Este es el procedimiento compartido y ejecutado por el usuario para validar SICL-Web. Ejecutarlo desde el servidor, en la ruta canónica:

```bash
cd /home/arki/ARKI/canonical/sicl-web || {
  echo "ERROR: SICL Web no encontrado"
  read -r -p "ENTER para volver"
  exit 1
}

LOG="/tmp/sicl-web-sqlite-mo47-$(date +%Y%m%d-%H%M%S).log"
exec > >(tee -a "$LOG") 2>&1

echo "=================================================="
echo "MO47 — VALIDACIÓN INTEGRAL SICL WEB"
echo "=================================================="
echo "Fecha: $(date -Is)"
echo "Rama: $(git branch --show-current)"
echo "HEAD: $(git rev-parse HEAD)"
echo

echo "--- 1. Suite completa Vitest ---"
pnpm exec vitest run
TEST_RESULT=$?

echo
echo "--- 2. Validación del diff ---"
git diff --check
DIFF_RESULT=$?

echo
echo "--- 3. Estado de cambios ---"
git status --short

echo
echo "--- 4. Resumen de cambios versionados ---"
git diff --stat

echo
echo "--- 5. Archivos SQLite existentes ---"
find drizzle/sqlite -maxdepth 3 -type f -print 2>/dev/null

echo
echo "--- 6. Verificación de configuración de producción ---"
grep -n -E 'mysql|mysql2|drizzle-orm/mysql|DATABASE_URL' server/db.ts drizzle.config.ts

echo
if [ "$TEST_RESULT" -eq 0 ] && [ "$DIFF_RESULT" -eq 0 ]; then
  echo "MO47 RESULT: PASS"
  echo "Suite completa y diff aprobados."
else
  echo "MO47 RESULT: FAIL"
  echo "Vitest exit: $TEST_RESULT"
  echo "Diff exit: $DIFF_RESULT"
fi

echo
echo "Log: $LOG"
echo "=================================================="
read -r -p "MO47 terminó. ENTER para volver al terminal..."
```

### 8.3 Ejecución resumida (sin pausa interactiva)

Para repetir la suite y guardar el log sin quedarse esperando ENTER:

```bash
cd /home/arki/ARKI/canonical/sicl-web || exit 1
LOG="/tmp/sicl-web-vitest-$(date +%Y%m%d-%H%M%S).log"
pnpm exec vitest run 2>&1 | tee "$LOG"
TEST_RESULT=${PIPESTATUS[0]}
git diff --check
DIFF_RESULT=$?
echo "Vitest exit: $TEST_RESULT"
echo "Diff exit: $DIFF_RESULT"
echo "Log: $LOG"
```

### 8.4 Resultado MO47 registrado

Según el log aportado:

- Vitest: **164 archivos aprobados**.
- Tests: **1,021 aprobados, 4 omitidos**.
- Duración de Vitest: **15.15 s**.
- `git diff --check`: aprobado.
- Resultado MO47: `PASS`.

El PASS significa que la suite que se ejecutó y el chequeo de diff terminaron correctamente. **No certifica que SQLite sea el backend principal de SICL-Web ni que la migración MySQL → SQLite esté completa.**

La inspección del log confirma que:
- `server/db.ts` importa `drizzle-orm/mysql2`.
- `drizzle.config.ts` declara `dialect: "mysql"`.
- `DATABASE_URL` sigue siendo requerido por los comandos Drizzle.
- Se ejecutaron pruebas de repositorios SQLite y una integración HTTP aislada MO22 (13/13), sin MariaDB.

### 8.5 Cómo arrancar la aplicación (límite de evidencia)

MO47 valida pruebas, diff y configuración; **no arranca el servidor web ni demuestra el flujo de inicio de ARKI completo**. No se debe inventar un comando `dev`, `start` o Docker Compose sin revisar el `00_start.md` vigente y los scripts reales de `package.json`.

Para recuperar el procedimiento oficial:
```bash
cd /home/arki/ARKI/canonical/sicl-web
node -e 'console.log(JSON.stringify(require("./package.json").scripts,null,2))'
```

Revisar `00_start.md` y usar el comando de inicio allí documentado. Antes de arrancar servicios, comprobar variables requeridas y evitar imprimir valores secretos. Para el arranque integral ARKI (SICL-Web + SICL-Core + ACS), hace falta registrar el procedimiento vigente de `00_start.md`; MO47 por sí solo solo cubre la suite de SICL-Web.

### 8.6 Evidencia pendiente para prueba total

- Ejecutar el procedimiento de arranque oficial de ARKI y guardar log.
- Confirmar health/readiness de Web, Core y ACS, con sus URLs/puertos documentados.
- Ejecutar las pruebas E2E de integración Web → Core → AGK → ACS.
- Confirmar la configuración de backend activa sin exponer secretos.
- Mantener SQLite como **aislado/no principal** hasta que routers, servicios, datos y runtime hayan pasado las pruebas de migración.
- Adjuntar logs y resultados. No declarar PASS global con MO47 solamente.


## 9. Expediente arquitectónico activo — Restaurante Salaverry

### 9.1 Datos de entrada confirmados por el usuario

- **Ubicación:** Trujillo, Perú.
- **Jurisdicción:** Salaverry.
- **Tipología:** restaurante para 400 comensales.
- **Sitio:** frente al mar.
- **Intención de diseño:** belleza orgánica.
- **Relaciones funcionales y espaciales:** deben ser derivadas por ARKI, no inventadas manualmente como resultado final.

Estos datos constituyen el brief inicial. No se han suministrado aquí dimensiones del terreno, orientación, topografía, retiros, accesos, normativa específica, aforo operativo desagregado, condiciones ambientales medidas ni programa detallado de ambientes. Deben permanecer como desconocidos hasta que se incorporen fuentes o decisiones explícitas.

### 9.2 Cadena de ejecución que debe seguir ARKI

`Brief del proyecto → Brain/Wave 1 → D6.2 → D6.3 → D6.4 → D6.5 → D7 → D8 → D9 → D10`

Reglas de interpretación:

1. Brain puede producir actividades, relaciones, tensiones, partis/topologías e hipótesis; la ausencia de geometría final en Brain no significa que ARKI no pueda producir volumetría posteriormente.
2. D6.2 debe derivar requisitos, estrategias, realizaciones, topología, incertidumbres y trazabilidad a partir de las entradas reales. Su `PASS` interno no equivale a aprobación del proyecto ni a completitud arquitectónica.
3. D6.3 debe recibir el expediente del restaurante y generar/evaluar la volumetría y geometría que permita su contrato vigente. Las salidas deben identificarse como exploratorias, hipotéticas o validadas según la evidencia real.
4. D6.4–D10 se ejecutarán después de revisar los resultados de D6.2/D6.3 y sus dependencias. No declarar estas fases ejecutadas antes de disponer de logs/resultados.
5. No sustituir la intención “belleza orgánica” por una forma arbitraria. ARKI debe producir alternativas trazables y mostrar qué datos, reglas o decisiones humanas sustentan cada alternativa.
6. No inventar dimensiones, restricciones normativas, condiciones del sitio ni parámetros de diseño. Mantenerlos como `UNKNOWN`/pendientes cuando no exista evidencia.

### 9.3 Estado técnico del caso al actualizar este handoff

Se revisaron fragmentos del harness D6.2, del puente D6.3 y del adaptador D6.3→D2 compartidos en la conversación. La evidencia visible permite afirmar:

- D6.2 deriva requisitos relacionales y de asignación; preserva campos desconocidos y declara que una relación funcional no implica por sí misma geometría.
- D6.2 produce estrategias/realizaciones hipotéticas y topología con trazabilidad.
- El puente D6.3→D2 acepta un polígono rectangular local 2D cerrado, con cuatro vértices únicos, unidades en metros y elevación/altura en milímetros; lo transforma en un volumen rectangular extruido. Este contrato no demuestra por sí solo una volumetría orgánica del restaurante.
- El código y las pruebas D6.3 previamente localizados contienen una prueba de exploración geométrica para otra tipología. Esa prueba no debe presentarse como ejecución del restaurante de Salaverry.
- `executeCanonicalBrainAndD62` persiste Brain y D6.2 en Core y verifica que la versión canónica no cambie; no ejecuta D6.3–D10 en la función mostrada.

**Estado del expediente:** brief identificado; ejecución canónica Brain/D6.2 para este restaurante no acreditada por un resultado completo; D6.3 para este restaurante no acreditada; D6.4–D10 pendientes de ejecución y evidencia.

### 9.4 Registro de evidencia requerido por fase

Para cada fase registrar, sin resumirlo como “completado” por la mera existencia de código:

| Fase | Evidencia mínima | Estado actual del caso |
|---|---|---|
| Brief | Entrada exacta y fuente/autor | Datos iniciales registrados; programa y sitio incompletos |
| Brain/Wave 1 | Input, output, execution ID y persistencia | Pendiente de resultado específico del restaurante |
| D6.2 | Input/output, requisitos, unknowns, deficits, estrategias, realizaciones, topología y execution ID | Código inspeccionado; ejecución específica pendiente |
| D6.3 | Alternativas, geometría/volumetría, validaciones, fallos y trazabilidad | Código/contrato inspeccionado; restaurante pendiente |
| D6.4–D10 | Resultado de cada fase, dependencias, validaciones y decisión humana cuando aplique | Pendientes |

### 9.5 Próxima secuencia operativa — sin crear ramas nuevas

1. Confirmar el estado actual del working tree y preservar los archivos no rastreados/backups.
2. Construir un input del restaurante usando solo los datos confirmados; declarar unknowns explícitos.
3. Ejecutar Brain y D6.2 en el proyecto canónico existente, sin crear otro proyecto ni alterar snapshots. Registrar IDs de ejecución y respuesta de Core.
4. Revisar el resultado D6.2: relaciones, requisitos, incertidumbres y alternativas. No marcar como aprobado por un `PASS` de harness.
5. Adaptar/ejecutar D6.3 con el expediente real. Si el contrato actual solo admite rectángulos extruidos, documentar esa limitación y no etiquetar el resultado como forma orgánica.
6. Continuar D6.4–D10 únicamente con dependencias y entradas verificadas; registrar cada fase por separado.
7. Actualizar este handoff con resultados reales, IDs, logs y estado; no fabricar un PASS global.

### 9.6 Corrección de rutas y alcance

Repositorio canónico reportado: `/home/arki/ARKI/canonical/sicl-web`.

Handoff base: `00_HANDOFF_INICIO_ARKI.md` (este documento compartido) y handoff generado del repositorio `ARKI_HANDOFF.md`.

El helper local `~/ARKI/handoff/actualizar-handoff.sh` fue reportado apuntando a `~/ARKI/repos/sicl-web`, ruta que no corresponde al repositorio canónico actual. No ejecutarlo hasta corregir y verificar su destino. La actualización de `ARKI_HANDOFF.md` debe realizarse en el generador que lo produce, no solo editando el Markdown generado.

**No se afirma que este archivo haya sido instalado, committeado o sincronizado en el servidor/repositorio.** Esta revisión actualiza el documento local compartido; la incorporación al repositorio canónico requiere ejecutar y verificar allí la operación.
