#!/bin/sh
set -e

# Determinar puerto válido
PORT_TO_USE=8000
if [ -n "$PORT" ] && [ "$PORT" -eq "$PORT" ] 2>/dev/null; then
    PORT_TO_USE="$PORT"
else
    echo "WARN: PORT='$PORT' is not a valid integer. Falling back to 8000."
fi

echo "INFO: starting uvicorn on port $PORT_TO_USE"
exec uvicorn api.main:app --host 0.0.0.0 --port "$PORT_TO_USE"
