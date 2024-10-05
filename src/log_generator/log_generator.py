import os
import random
import datetime
import time
import logging

class LogGenerator:
    def __init__(self):
        # Load environment variables and parameters
        self.log_batch_size = int(os.getenv("LOG_BATCH_SIZE"))
        self.log_interval_seconds = int(os.getenv("LOG_INTERVAL_SECONDS"))
        self.log_file_path = os.getenv("LOG_FILE_PATH", "api_requests.log")
        self.max_logs = int(os.getenv("MAX_LOGS_TO_GENERATE"))  # Stop after max number of logs

        # Log Data initialization
        random.seed(42)  # Set seed for reproducibility
        self.customer_ids = [f"cust_{i}" for i in range(1, 51)]
        self.request_paths = ["/api/v1/resource1", "/api/v1/resource2", "/api/v1/resource3", "/api/v1/resource4"]
        self.status_codes = [200, 201, 400, 401, 403, 404, 500]
        self.durations = [random.uniform(0.1, 2.0) for _ in range(self.max_logs)]

        # Logging
        self.configure_logging()

    @staticmethod
    def configure_logging():
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s %(levelname)s: %(message)s',
            handlers=[
                logging.FileHandler('log_generator.log'),
                logging.StreamHandler()
            ]
        )

    def generate_timestamp(self):
        """Generates a random timestamp within the past 30 days."""
        past_days = 30
        start_date = datetime.datetime.now() - datetime.timedelta(days=past_days)
        random_seconds = random.randint(0, past_days * 24 * 60 * 60)
        return start_date + datetime.timedelta(seconds=random_seconds)

    def generate_log_entry(self):
        """Generates a single log entry."""
        timestamp = self.generate_timestamp().strftime("%Y-%m-%d %H:%M:%S")
        customer_id = random.choice(self.customer_ids)
        request_path = random.choice(self.request_paths)
        status_code = random.choice(self.status_codes)
        duration = f"{random.choice(self.durations):.3f}"
        return f"{timestamp} {customer_id} {request_path} {status_code} {duration}\n"

    def ingest_logs(self):
        """
        This function simulates a real life scenario where logs keep growing in a .log file.
        It generates logs in batches based on LOG_BATCH_SIZE per LOG_INTERVAL_SECONDS and append file at LOG_FILE_PATH.
        For example: LOG_BATCH_SIZE=100 & LOG_INTERVAL_SECONDS=10 will append 100 logs to the log file located at
        LOG_FILE_PATH every 10 seconds. These values can be passed as env vars to simulate expected log load.
        """
        total_logs_written = 0

        logging.info(f"Starting log generation with batch size {self.log_batch_size} and interval {self.log_interval_seconds}s")

        while total_logs_written < self.max_logs:
            with open(self.log_file_path, "a") as log_file:
                for _ in range(self.log_batch_size):
                    if total_logs_written >= self.max_logs:
                        logging.info(f"Reached max log limit of {self.max_logs}. Stopping log generation.")
                        return
                    log_file.write(self.generate_log_entry())
                    total_logs_written += 1

            logging.info(f"Generated {self.log_batch_size} logs. Total logs written: {total_logs_written}")
            time.sleep(self.log_interval_seconds)

        logging.info("Log generation completed.")


if __name__ == '__main__':
    import time
    time.sleep(10)  # HACK: extra wait time for log_processor to initialise
    log_generator = LogGenerator()
    log_generator.ingest_logs()
