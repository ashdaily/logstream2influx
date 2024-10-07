import logging
import asyncio
from abc import ABC, abstractmethod
from dateutil import parser as dateutil_parser
from typing import List
from storage import InfluxDBStorage


class LogHandlerBase(ABC):
    @abstractmethod
    async def handle_log(self, log_lines: List[str]):
        pass


class LogHandler(LogHandlerBase):
    def __init__(self):
        pass

    async def handle_log(self, log_lines: List[str]):
        await self._handle_log(log_lines)

    async def _handle_log(self, log_lines: List[str]):
        logging.info(f"LogHandler received {len(log_lines)} logs for processing.")
        ready_logs = []
        for log_line in log_lines:
            log_data = self._process_log(log_line)
            if log_data:
                ready_logs.append(log_data)

        logging.info(f"LogHandler ready to save {len(ready_logs)} logs in DB.")

        # Ensure client is initialized within an async context
        influx_storage = InfluxDBStorage()
        await influx_storage.initialize()
        await influx_storage.store_log(ready_logs)
        await influx_storage.close()

    def _process_log(self, log_line: str):
        try:
            parts = log_line.split()
            if len(parts) >= 6:
                timestamp_str = f"{parts[0]} {parts[1]}"
                timestamp = dateutil_parser.isoparse(timestamp_str)
                customer_id = parts[2]
                request_path = parts[3]
                status_code = int(parts[4])
                duration = float(parts[5])

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
                    "time": timestamp.isoformat() + "Z"
                }
                logging.debug(f"Processed log data: {record}")
                return record
            else:
                logging.info(f"Invalid log line format: {log_line}")
        except Exception as e:
            logging.error(f"Error processing log line: {log_line}. Error: {e}")
            return None
