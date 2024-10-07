#!/bin/bash
# Check if the log file exists
./cleanup.sh

GEN_LOG_FILE="./src/log_generator/api_requests.log"
PROCESSOR_LOG_FILE="./src/log_processor/log_processor.log"
LOG_GEN_LOG_FILE="./src/log_generator/log_generator.log"

if [ -f "$GEN_LOG_FILE" ]; then
    echo "$GEN_LOG_FILE exists."
else
    echo "$GEN_LOG_FILE does not exist. Creating an empty log file."
    touch "$GEN_LOG_FILE"
    echo "$GEN_LOG_FILE has been created."
fi

if [ -f "$PROCESSOR_LOG_FILE" ]; then
    echo "$PROCESSOR_LOG_FILE exists."
else
    echo "$PROCESSOR_LOG_FILE does not exist. Creating an empty log file."
    touch "$PROCESSOR_LOG_FILE"
    echo "$PROCESSOR_LOG_FILE has been created."
fi

if [ -f "$LOG_GEN_LOG_FILE" ]; then
    echo "$LOG_GEN_LOG_FILE exists."
else
    echo "$LOG_GEN_LOG_FILE does not exist. Creating an empty log file."
    touch "$LOG_GEN_LOG_FILE"
    echo "$LOG_GEN_LOG_FILE has been created."
fi


echo "Starting Docker Compose services..."
docker compose -f compose.yaml --env-file .env.local up