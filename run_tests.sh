#!/bin/bash

echo "Preparing containers for testing ...."
./testmode.sh

# cleanup will run after the script ends, even on error
trap './cleanup.sh' EXIT

echo "Starting tests in the 'log_processor' container..."
docker compose -f compose.yaml --env-file .env.local run log_processor python -m unittest

echo "Starting tests in the 'rate_api' container..."
docker compose -f compose.yaml --env-file .env.local run rated_api python -m unittest
