#!/bin/bash
# Check if the log file exists
LOG_FILE="./src/log_generator/api_requests.log"

if [ -f "$LOG_FILE" ]; then
    echo "$LOG_FILE exists."
else
    echo "$LOG_FILE does not exist. Creating an empty log file."
    touch "$LOG_FILE"
    echo "$LOG_FILE has been created."
fi

# Build and run the services using Docker Compose
echo "Building Docker Compose services..."
docker compose --env-file src/config/.env.local build --no-cache

echo "Starting Docker Compose services..."
docker compose --env-file src/config/.env.local up