#!/bin/bash

./cleanup.sh

echo "Building Docker services..."
docker compose -f compose.yaml --env-file .env.local build log_processor rated_db rated_api --no-cache

echo "Starting Docker services..."
docker compose -f compose.yaml --env-file .env.local up -d log_processor rated_db rated_api

check_container_health() {
  container_name=$1
  while true; do
    health_status=$(docker inspect --format='{{.State.Health.Status}}' "$container_name" 2>/dev/null)

    if [[ "$health_status" == "" ]]; then
      state=$(docker inspect --format='{{.State.Status}}' "$container_name")
      if [[ "$state" == "running" ]]; then
        echo "$container_name is running but health checks are not defined, proceeding ..."
        return 0
      else
        echo "$container_name is not running, waiting ..."
      fi
    elif [[ "$health_status" == "healthy" ]]; then
      echo "$container_name is healthy !"
      return 0
    else
      echo "$container_name is not ready yet (current status: $health_status), waiting ..."
    fi
    sleep 5
  done
}

# Check for container readiness
check_container_health "rated_db"
check_container_health "log_processor"