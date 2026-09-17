# Despliegue de SICL Core en Railway

## Estado y alcance

El repositorio `YvanCastilloQuezada/sicl-core` contiene la API FastAPI en `api.main:app`. El servicio se inicia mediante `Procfile` y escucha en `0.0.0.0:$PORT`, como exige Railway. La ruta de SQLite es configurable mediante `SICL_DB_PATH`; para persistencia real debe apuntar a un volumen persistente de Railway. Una instancia efímera sin volumen no es suficiente para declarar persistencia E2E.

## 1. Crear el servicio

1. Inicie sesión en [Railway](https://railway.app/).
2. Cree un proyecto nuevo.
3. Seleccione **Deploy from GitHub repo**.
4. Autorice GitHub si Railway lo solicita.
5. Seleccione `YvanCastilloQuezada/sicl-core`.
6. Railway detectará el `Procfile` y construirá el servicio Python.
7. En **Settings → Networking**, genere un dominio público Railway. No fabrique una URL antes de que Railway la muestre.

## 2. Variables de entorno

Configure estas variables en **Variables** del servicio:

| Variable | Valor | Observación |
|---|---|---|
| `SICL_DB_PATH` | `/data/sicl/sicl.sqlite` | Ruta recomendada dentro del volumen persistente |
| `DATABASE_URL` | `./sicl.db` | Alternativa compatible para una primera ejecución sin `SICL_DB_PATH` |
| `SICL_CORS_ORIGINS` | `https://<dominio-real-del-frontend>` | Sustituir por el origen real; sin barra final |
| `PORT` | Gestionada por Railway | No fijar manualmente salvo que Railway lo requiera |

Si se configuran ambas, `SICL_DB_PATH` tiene prioridad. Para una prueba inicial puede configurarse `DATABASE_URL=./sicl.db`; para producción con volumen, use `SICL_DB_PATH=/data/sicl/sicl.sqlite`.

### Persistencia

Añada un **Volume** al servicio y móntelo en `/data/sicl`. Sin volumen, SQLite puede perderse cuando Railway reprograme o reinicie el contenedor. La persistencia del volumen debe probarse después del primer despliegue.

## 3. Verificación del despliegue

Después de que Railway muestre el dominio público real:

```bash
export CORE_URL="https://<dominio-real-de-railway>"
curl -fsS "$CORE_URL/health"
curl -i -X OPTIONS "$CORE_URL/projects" \
  -H 'Origin: https://<dominio-real-del-frontend>' \
  -H 'Access-Control-Request-Method: POST'
```

La primera respuesta debe indicar `status: ok`. La respuesta CORS debe incluir `Access-Control-Allow-Origin` con el origen configurado.

## 4. Prueba funcional mínima

No reutilice datos productivos. Use un identificador de prueba:

```bash
curl -fsS -X POST "$CORE_URL/projects" \
  -H 'Content-Type: application/json' \
  -d '{"project_id":"TEST-E2E-001","name":"SICL Railway Smoke Test"}'

curl -fsS -X POST "$CORE_URL/commands" \
  -H 'Content-Type: application/json' \
  -d '{"project_id":"TEST-E2E-001","command":"/OBJECTIVE SET CLIMATE MAXIMIZE 80"}'

curl -fsS "$CORE_URL/projects/TEST-E2E-001"
```

Los nombres exactos de campos deben confirmarse contra la respuesta de OpenAPI de la instancia desplegada. Si un comando devuelve error de contrato, no se debe cambiar el Core en producción para forzar la prueba.

## 5. Persistencia después de reinicio

1. Crear `TEST-PERSIST-001` y registrar un dato de prueba.
2. Confirmar que `GET /projects/TEST-PERSIST-001` responde correctamente.
3. Reiniciar el servicio desde Railway.
4. Repetir el `GET`.
5. Marcar PASS solo si el dato se conserva y el volumen está montado en `/data/sicl`.

## 6. Conectar el frontend

En GitHub, abra `YvanCastilloQuezada/sicl-web` y vaya a:

`Settings → Secrets and variables → Actions → Variables → New repository variable`

Configure:

```text
Name: VITE_API_URL
Value: https://<dominio-real-de-railway>
```

La URL no es un secreto porque debe llegar al navegador. No introduzca tokens en `VITE_*`. El build de GitHub Actions leerá `vars.VITE_API_URL`.

Después, compruebe que el frontend configure como origen CORS exactamente su dominio público real. Un dominio `manus.space` y un dominio GitHub Pages son orígenes distintos.

## 7. Criterio de salida

El despliegue puede marcarse **READY FOR REMOTE E2E** cuando `/health`, CORS, la prueba funcional, la persistencia después de reinicio y la conexión del frontend hayan sido verificadas con la URL real. No se debe declarar `E2E VERIFIED` únicamente porque Railway haya completado el build.


## Estado vigente de capacidades — actualización 2026-09-16

> Esta sección supersede las afirmaciones históricas de este documento que indiquen que GIS, BIM o el Copiloto local están fuera de alcance. El baseline vigente incluye RFC-027, RFC-028 y RFC-029.

El Core actual incluye importación IFC física de solo lectura, snapshots BIM persistentes, BIMChangeSet en modo PREVIEW, detección de conflictos BIM, contratos de exportación que exigen HumanReview, persistencia SQLite de ParcelSnapshot, catálogo GIS por jurisdicción, caducidad y ParcelBoundaryConflict, consulta OGC API Features y traducción Ollama a comandos SICL en modo PREVIEW_ONLY.

Estas capacidades no otorgan autoridad automática. El Copiloto no ejecuta comandos ni crea decisiones. Los adaptadores Revit y Archicad requieren sus hosts y SDKs nativos. La exportación BIM queda pendiente de ejecución externa después de una HumanReview aprobada. Las fuentes catastrales requieren registro explícito, licencia y validación humana.

La referencia operativa es [`PRODUCTION_CORE_DEPLOYMENT_MANUAL.md`](PRODUCTION_CORE_DEPLOYMENT_MANUAL.md). La suite E2E se ejecuta con `PYTHONPATH=.:src pytest -q tests/test_e2e_ollama_sicl.py -ra`.
