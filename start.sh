#!/bin/bash
# Start Redis server in the background
redis-server --daemonize yes

# Wait for Redis to be ready
until redis-cli ping | grep -q PONG; do
  echo "Waiting for Redis to start..."
  sleep 1
done
echo "Redis is ready!"

# Start the application
uvicorn src.api.main:app --host 0.0.0.0 --port 8000 