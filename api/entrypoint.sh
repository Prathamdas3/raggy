#!/bin/sh

if [ "$MODE" = "api" ]; then
    echo "Starting FastAPI server..."
    uv run uvicorn app.main:app --host 0.0.0.0 --port 8000
elif [ "$MODE" = "worker" ]; then
    echo "Starting background worker..."
    uv run python -m app.worker
else
    echo "ERROR: Unknown MODE='$MODE'"
    exit 1
fi
