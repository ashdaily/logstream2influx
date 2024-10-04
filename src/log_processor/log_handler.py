import logging
from abc import ABC, abstractmethod
from dateutil import parser as dateutil_parser
from typing import List


class LogHandlerBase(ABC):
    @abstractmethod
    def handle_log(self, log_lines: List[str]):
        pass


class LogHandler(LogHandlerBase):
    def __init__(self, storage):
        self.storage = storage

    def handle_log(self, log_lines: List[str]):
        logging.info(f"LogHandler received {len(log_lines)}")
        ready_logs = []
        for log_line in log_lines:
            log_data = self._process_log(log_line)
            if log_data:
                ready_logs.append(log_data)

        logging.info(f"LogHandler ready to save {len(ready_logs)} logs in DB")
        self.storage.store_log(ready_logs)

    def _process_log(self, log_line: str):
        try:
            parts = log_line.split()
            if len(parts) >= 6:
                timestamp_str = f"{parts[0]} {parts[1]}"
                # faster date parsing
                timestamp = dateutil_parser.isoparse(timestamp_str)
                customer_id = parts[2]
                request_path = parts[3]
                status_code = int(parts[4])
                duration = float(parts[5])

                # Determine if the request was successful (status_code 2xx or 3xx)
                success = 1 if 200 <= status_code < 400 else 0
                record = {
                    "measurement": "api_requests",
                    "tags": {
                        "customer_id": customer_id,
                        "success": success
                    },
                    "fields": {
                        "duration": duration,
                        "status_code": status_code,
                        "request_path": request_path
                    },
                    "time":  timestamp.isoformat() + "Z"
                }
                return record
            else:
                logging.debug(f"Invalid log line: {log_line}")
        except Exception as e:
            logging.debug(f"Error processing log line: {log_line}. Error: {e}")
            return None
