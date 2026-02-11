#!/bin/bash
export PYTHONPATH=/app
# Use the PORT provided by the environment (Render), or default to 7860 (Hugging Face)
PORT=${PORT:-7860}
echo "Starting app on port $PORT..."
uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT
