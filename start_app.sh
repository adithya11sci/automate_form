#!/bin/bash
export PYTHONPATH=/app
# Default to port 5000 as requested by the user
PORT=${PORT:-5000}
echo "Starting app on port $PORT..."
uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT
