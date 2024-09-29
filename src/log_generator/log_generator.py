import os
import random
import datetime
import time
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s: %(message)s',
    handlers=[
        logging.FileHandler('log_generator.log'),
        logging.StreamHandler()
    ]
)

# These env variable are used to continuously append logs so bytewax stream can continue streaming logs to influx db.
log_batch_size = int(os.getenv("LOG_BATCH_SIZE", 100))
log_interval_seconds = int(os.getenv("LOG_INTERVAL_SECONDS", 10))
log_file_path = os.getenv("LOG_FILE_PATH", "api_requests.log")
max_logs = 100_000_000  # We consciously want to stop the simulation after 100 million logs.

random.seed(42)  # Set seed before generating durations

# Parameters
customer_ids = [f"cust_{i}" for i in range(1, 51)]
request_paths = ["/api/v1/resource1", "/api/v1/resource2", "/api/v1/resource3", "/api/v1/resource4"]
status_codes = [200, 201, 400, 401, 403, 404, 500]
durations = [random.uniform(0.1, 2.0) for _ in range(max_logs)]


# Function to generate random timestamp
def generate_timestamp():
    start_date = datetime.datetime.now() - datetime.timedelta(days=30)
    random_seconds = random.randint(0, 30*24*60*60)
    return start_date + datetime.timedelta(seconds=random_seconds)


def generate_logs():
    """
    This function simulates a real life production server that keeps ingesting logs to a .log file.

    It generates logs in batches based on log_batch_size per log_interval_seconds and append file at log_file_path.

    For example: log_batch_size=100 & log_interval_seconds=10 will append 100 logs to the log file located at
    log_file_path every 10 seconds. These values can be passed as env vars to simulate expected log load.

    :return: None
    """
    total_logs_written = 0

    logging.info(f"Starting log generation with batch size {log_batch_size} and interval {log_interval_seconds}s")

    while total_logs_written < max_logs:
        with open(log_file_path, "a") as log_file:
            for _ in range(log_batch_size):
                if total_logs_written >= max_logs:
                    logging.info(f"Reached max log limit of {max_logs}. Stopping log generation.")
                    return
                timestamp = generate_timestamp().strftime("%Y-%m-%d %H:%M:%S")
                customer_id = random.choice(customer_ids)
                request_path = random.choice(request_paths)
                status_code = random.choice(status_codes)
                duration = f"{random.choice(durations):.3f}"
                log_file.write(f"{timestamp} {customer_id} {request_path} {status_code} {duration}\n")
                total_logs_written += 1

        logging.info(f"Generated {log_batch_size} logs. Total logs written: {total_logs_written}")
        time.sleep(log_interval_seconds)

    logging.info("Log generation completed.")


if __name__ == '__main__':
    generate_logs()
