# SICL Core API v1.0

Capa REST FastAPI sobre el Core CLI existente. La API no duplica reglas de dominio: traduce requests a comandos SICL y devuelve respuestas estructuradas.

## Ejecutar

Desde `/home/ubuntu/sicl-core-v1.0`:

```bash
uvicorn api.main:app --reload --port 8000
```

Health check:

```bash
curl http://localhost:8000/health
```

## Endpoints

| Método | Ruta | Propósito |
|---|---|---|
| GET | `/projects` | Lista proyectos |
| POST | `/projects` | Crea un proyecto |
| GET | `/projects/{project_id}` | Recupera un proyecto |
| PUT | `/projects/{project_id}` | Actualiza la etapa |
| DELETE | `/projects/{project_id}` | Cierre lógico; no elimina historial |
| POST | `/commands` | Ejecuta un comando SICL |

Ejemplo:

```bash
curl -X POST http://localhost:8000/projects \
  -H 'content-type: application/json' \
  -d '{"project_id":"UPAO-001","name":"Plaza Center","actor":"architect"}'
```

## CORS

Por defecto se permite `*` para desarrollo. En despliegue se recomienda configurar:

```bash
export SICL_CORS_ORIGINS=https://siclcc-cxipx7sy.manus.space
```

## Pruebas

```bash
python3 -m pytest -ra
```

La API mantiene la persistencia SQLite y los eventos append-only del Core. `DELETE /projects/{id}` es un cierre lógico (`STAGE=CLOSED`) para no destruir estado ni historial.
