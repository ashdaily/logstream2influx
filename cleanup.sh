#!/bin/bash

LOG_FILE="./src/log_generator/api_requests.log"
PROCESSOR_LOG="./src/log_processor/log_processor.log"
GENERATOR_LOG="./src/log_generator/log_generator.log"
INFLUX_VOLUME="./influx-volume"

# Step 1: Empty the api_requests.log file
if [ -f "$LOG_FILE" ]; then
    echo "Emptying $LOG_FILE..."
    > "$LOG_FILE"
    echo "$LOG_FILE has been emptied."
else
    echo "$LOG_FILE does not exist, skipping."
fi

# Step 2: Stop and remove all containers, networks, volumes using Docker Compose
echo "Stopping and removing all containers, networks, and volumes..."
docker compose --env-file .env.local down -v

# Step 3: Remove influx-volume folder and its contents
if [ -d "$INFLUX_VOLUME" ]; then
    echo "Removing $INFLUX_VOLUME and its contents..."
    rm -rf "$INFLUX_VOLUME"
    echo "$INFLUX_VOLUME has been removed."
else
    echo "$INFLUX_VOLUME does not exist, skipping."
fi

# Step 4: Remove log_processor.log
if [ -f "$PROCESSOR_LOG" ]; then
    echo "Removing $PROCESSOR_LOG..."
    rm -f "$PROCESSOR_LOG"
    echo "$PROCESSOR_LOG has been removed."
else
    echo "$PROCESSOR_LOG does not exist, skipping."
fi

# Step 5: Remove log_generator.log
if [ -f "$GENERATOR_LOG" ]; then
    echo "Removing $GENERATOR_LOG..."
    rm -f "$GENERATOR_LOG"
    echo "$GENERATOR_LOG has been removed."
else
    echo "$GENERATOR_LOG does not exist, skipping."
fi

echo "Cleanup complete."
