import os
from dotenv import load_dotenv

load_dotenv()

# InfluxDB Configuration
INFLUXDB_URL = os.getenv("INFLUXDB_URL")
INFLUXDB_TOKEN = os.getenv("DOCKER_INFLUXDB_INIT_ADMIN_TOKEN")
INFLUXDB_ORG = os.getenv("DOCKER_INFLUXDB_INIT_ORG")
INFLUXDB_BUCKET = os.getenv("DOCKER_INFLUXDB_INIT_BUCKET")

# Log Processing Configuration
LOG_FILE_PATH = os.getenv("LOG_FILE_PATH", "/log_generator/api_requests.log")
LOG_BATCH_SIZE = int(os.getenv("LOG_BATCH_SIZE", 10000))  # Increased batch size
LOG_FLUSH_INTERVAL_MS = int(os.getenv("LOG_FLUSH_INTERVAL_MS", 100))  # Reduced flush interval in milliseconds

# Logging Configuration
LOGGING_LEVEL = os.getenv("LOGGING_LEVEL", "INFO").upper()

# Bytewax
STREAM_MAX_SIZE = int(os.getenv("STREAM_MAX_SIZE", 100000))
STREAM_MAX_WAIT_TIME_IN_SECONDS = float(os.getenv("STREAM_MAX_WAIT_TIME_IN_SECONDS", 1))