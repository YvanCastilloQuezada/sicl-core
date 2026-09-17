# Manual de configuración y despliegue productivo del Core SiMS-DeI

**Versión:** 2.10

**Repositorio:** `YvanCastilloQuezada/sicl-core`

**Baseline recomendado:** `sims-dei-2.10-gis-bim-completion`

## 1. Alcance

Este manual explica cómo desplegar el Core SICL como servicio FastAPI persistente. El Core registra proyectos, evidencia, análisis, snapshots GIS, operaciones BIM y propuestas del Copiloto. El Core no permite que un modelo de lenguaje cree decisiones humanas automáticamente.

El despliegue productivo requiere una URL HTTPS pública, persistencia SQLite en un volumen y un token de servicio secreto. El token se usa únicamente entre el proxy server-side del frontend y el Core.

## 2. Requisitos previos

Se necesita una cuenta del proveedor de hosting, acceso al repositorio GitHub, Python 3.11 o superior para pruebas locales y un dominio o URL HTTPS generada por el proveedor. Para producción con SQLite se necesita un volumen persistente.

El commit de referencia es:

```text
6a6021811d2764c67b1301d3df2cd776136ee52b
```

El tag equivalente es:

```text
sims-dei-2.10-gis-bim-completion
```

## 3. Preparar el repositorio

Clone el repositorio y seleccione el tag de producción:

```bash
git clone https://github.com/YvanCastilloQuezada/sicl-core.git
cd sicl-core
git checkout sims-dei-2.10-gis-bim-completion
```

Verifique el estado:

```bash
PYTHONPATH=.:src pytest -q -ra
python3 -m compileall -q src api tests
git diff --check
```

El criterio esperado es **239 pruebas pasando**, compilación correcta y ningún error de formato.

## 4. Archivos de arranque

El repositorio contiene un `Procfile` compatible con Railway y otros proveedores que soportan Procfiles:

```text
web: uvicorn api.main:app --host 0.0.0.0 --port ${PORT:-8000}
```

El servicio debe escuchar en `0.0.0.0` y en el puerto proporcionado por la variable `PORT`. No fije exclusivamente el puerto `8000` en producción.

## 5. Crear el servicio

En Railway, cree un proyecto, seleccione **Deploy from GitHub repo** y elija `YvanCastilloQuezada/sicl-core`. Seleccione la rama `main` o el tag de release después de verificar el commit. Genere un dominio público desde la sección de networking. No escriba manualmente una URL que Railway todavía no haya generado.

La misma configuración puede aplicarse a otro proveedor que ejecute el `Procfile`, siempre que soporte variables de entorno, HTTPS, health checks y volumen persistente.

## 6. Variables de entorno

Configure las siguientes variables en el panel de secretos del proveedor:

| Variable | Valor | Obligatorio |
|---|---|---:|
| `SICL_CORE_SERVICE_TOKEN` | Token largo, aleatorio y privado | Sí |
| `SICL_DB_PATH` | `/data/sicl/sicl.sqlite` | Sí con volumen |
| `SICL_CORS_ORIGINS` | Origen HTTPS exacto del frontend | Sí |
| `PORT` | Lo gestiona el proveedor | No fijarlo manualmente |
| `OLLAMA_BASE_URL` | URL de Ollama, si se usa Copiloto | Solo para Copiloto |
| `OLLAMA_MODEL` | Modelo local aprobado | Solo para Copiloto |

`DATABASE_URL=./sicl.db` puede utilizarse para una primera prueba, pero no debe sustituir al volumen persistente en producción.

Nunca configure `SICL_CORE_SERVICE_TOKEN` como variable `VITE_*`. Nunca lo incluya en código cliente, HTML, logs o respuestas JSON.

## 7. Configurar persistencia

Añada un volumen y móntelo en `/data/sicl`. Configure:

```text
SICL_DB_PATH=/data/sicl/sicl.sqlite
```

Reiniciar el contenedor sin un volumen puede eliminar los datos SQLite. La persistencia solo se considera verificada después de reiniciar el servicio y recuperar un proyecto de prueba.

## 8. Configurar CORS

Configure únicamente el origen real del frontend:

```text
SICL_CORS_ORIGINS=https://frontend.example.com
```

No use `*` en producción si se necesitan credenciales o control estricto de orígenes. No añada una barra final si el navegador presenta el origen sin ella.

## 9. Verificación inicial

Después del despliegue, sustituya `CORE_URL` por la URL HTTPS generada por el proveedor:

```bash
export CORE_URL="https://core.example.com"
export SICL_CORE_SERVICE_TOKEN="<introducir-localmente>"

curl -fsS "$CORE_URL/health"
curl -fsS "$CORE_URL/v1/health" \\
  -H "Authorization: Bearer $SICL_CORE_SERVICE_TOKEN"
```

Resultados esperados:

```json
{"status":"ok","service":"sicl-core-api"}
```

Y para `/v1/health`, un envelope con `status: OK`.

## 10. Verificar CORS

```bash
curl -i -X OPTIONS "$CORE_URL/projects" \\
  -H 'Origin: https://frontend.example.com' \\
  -H 'Access-Control-Request-Method: POST'
```

La respuesta debe incluir `Access-Control-Allow-Origin: https://frontend.example.com`.

## 11. Smoke test funcional

Use identificadores que no pertenezcan a usuarios reales:

```bash
curl -fsS -X POST "$CORE_URL/projects" \\
  -H 'Content-Type: application/json' \\
  -d '{"project_id":"DEPLOY-SMOKE-001","name":"SiMS-DeI deployment smoke test","actor":"deployment-check"}'

curl -fsS "$CORE_URL/projects/DEPLOY-SMOKE-001"
```

Para rutas protegidas:

```bash
curl -fsS "$CORE_URL/v1/projects/DEPLOY-SMOKE-001/snapshot" \\
  -H "Authorization: Bearer $SICL_CORE_SERVICE_TOKEN"
```

## 12. Verificar GIS

```bash
curl -fsS -X POST "$CORE_URL/v1/projects/DEPLOY-SMOKE-001/gis/parcel-snapshots" \\
  -H 'Content-Type: application/json' \\
  -d '{"feature":{"type":"Feature","id":"PARCEL-SMOKE-001","properties":{"district":"Trujillo"},"geometry":{"type":"Point","coordinates":[0,0]}},"source_url":"https://example.test/ogc","jurisdiction":"PE-TRUJILLO"}'

curl -fsS "$CORE_URL/v1/projects/DEPLOY-SMOKE-001/gis/parcel-snapshots"
```

El resultado debe conservar `decision_created: false` y el estado `HUMAN_REVIEW_REQUIRED`.

## 13. Verificar Copiloto Ollama

El Copiloto requiere que Ollama esté accesible desde el entorno del Core. Configure `OLLAMA_BASE_URL` y `OLLAMA_MODEL`. Después pruebe:

```bash
curl -fsS -X POST "$CORE_URL/v1/copilot/translate" \\
  -H 'Content-Type: application/json' \\
  -d '{"text":"abre el proyecto DEPLOY-SMOKE-001"}'
```

La respuesta debe incluir:

```text
status: PREVIEW_ONLY
executed: false
decision_created: false
```

Si Ollama no está configurado, el resultado esperado es `COPILOT_NOT_CONFIGURED`. No convierta ese error en una ejecución alternativa silenciosa.

## 14. Verificar autoridad humana

El E2E no se considera aprobado si el Copiloto puede ejecutar directamente un comando o crear una decisión. Revise que:

1. El Copiloto solo devuelve una intención.
2. La intención contiene un comando candidato.
3. El usuario debe revisar y confirmar.
4. `HumanReview` queda registrada antes de `Decision`.
5. Las decisiones contienen actor y autoridad.
6. El evento de auditoría conserva la trazabilidad.

## 15. Verificar persistencia

Cree un proyecto y un snapshot de prueba. Reinicie el servicio desde el proveedor. Repita las consultas. Marque la persistencia como PASS únicamente si los datos permanecen y el volumen continúa montado.

## 16. Conectar el frontend

Configure `SICL_CORE_URL` y `SICL_CORE_SERVICE_TOKEN` como secretos server-side de WebDev. No coloque el token en `VITE_*`. El proxy server-side debe añadir el header Bearer cuando llama al Core.

Después del redeploy del frontend:

```bash
curl -I https://frontend.example.com/
curl -fsS https://frontend.example.com/api/core/health
```

El navegador no debe poder leer el token mediante `window`, HTML, source maps ni bundles.

## 17. Criterio de salida

El despliegue puede marcarse `READY FOR E2E` cuando health, CORS, smoke test, persistencia, GIS, Copiloto y proxy estén verificados. Solo puede marcarse `E2E VERIFIED` después de probar el flujo completo con un Core remoto real.

## 18. Operación y seguridad

Rote el token si aparece en logs, repositorios, capturas o bundles. Mantenga backups del volumen. Registre el commit desplegado. No promueva fuentes normativas a vigentes automáticamente. No permita que un LLM modifique proyectos, evaluaciones, recomendaciones o decisiones sin revisión explícita.

## References

[1]: https://fastapi.tiangolo.com/deployment/ "FastAPI deployment concepts"
[2]: https://docs.railway.com/ "Railway documentation"
[3]: https://docs.ollama.com/api/openai-compatibility "Ollama OpenAI compatibility documentation"
