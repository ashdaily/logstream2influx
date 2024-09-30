import logging
from abc import ABC, abstractmethod
from datetime import datetime


class LogHandler(ABC):
    @abstractmethod
    def handle_log(self, log_line: str):
        pass


class LogProcessor(LogHandler):
    """
    Processes raw log lines and converts them to structured data.
    """

    def __init__(self, storage):
        self.storage = storage

    def handle_log(self, log_line: str):
        log_data = self._process_log(log_line)
        if log_data:
            self.storage.store_log(log_data)

    def _process_log(self, log_line: str):
        """
        Parses a log line and returns structured log data.
        Expected format: '<timestamp> <customer_id> <request_path> <status_code> <duration>'
        Example: '2024-09-14 16:15:35 cust_5 /api/v1/resource4 403 0.772'
        """
        logging.info(f"{self}._process_log log_line: {log_line}")
        try:
            parts = log_line.split()

            if len(parts) >= 5:
                timestamp_str = f"{parts[0]} {parts[1]}"
                timestamp = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
                customer_id = parts[2]
                request_path = parts[3]
                status_code = int(parts[4])
                duration = float(parts[5])

                return {
                    "timestamp": timestamp.isoformat(),
                    "customer_id": customer_id,
                    "request_path": request_path,
                    "status_code": status_code,
                    "duration": duration
                }
            else:
                logging.warning(f"Invalid log line: {log_line}")
                return None
        except Exception as e:
            logging.error(f"Error processing log line: {log_line}. Error: {e}")
            return None