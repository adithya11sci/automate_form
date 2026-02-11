#!/bin/bash
export PYTHONPATH=/app
uvicorn backend.app.main:app --host 0.0.0.0 --port 7860
