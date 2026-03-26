#!/bin/bash
# Start DeerFlow in production mode

export PYTHONPATH=/app/backend
export DEER_FLOW_HOME=/data/deerflow
export DEER_FLOW_CONFIG_PATH=/app/config.yaml

# Create data directory
mkdir -p /data/deerflow

# Start the gateway
cd /app/backend
exec uv run uvicorn app.gateway.app:app --host 0.0.0.0 --port 8000
