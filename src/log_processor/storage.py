from influxdb_client import InfluxDBClient
from abc import ABC, abstractmethod
import logging
from config import INFLUXDB_TOKEN, INFLUXDB_BUCKET, INFLUXDB_ORG


class LogStorage(ABC):
    @abstractmethod
    def store_log(self, log_data: dict):
        pass


class InfluxDBStorage(LogStorage):
    def __init__(self, influx_client: InfluxDBClient):
        self.write_api = influx_client.write_api()
        logging.info(f"InfluxDB storage initialized with bucket: {INFLUXDB_BUCKET} and org: {INFLUXDB_ORG}")

    def store_log(self, log_data: dict):
        """
        Store parsed log data into InfluxDB using a dictionary format.
        FIXME: check if schema is alright, also check for cardinality.
        """
        logging.info(f"Storing log data in InfluxDB: {log_data}")
        influx_payload = {
            "measurement": "api_requests",
            "tags": {
                "customer_id": log_data["customer_id"]
            },
            "fields": {
                "request_path": log_data["request_path"],
                "status_code": log_data["status_code"],
                "duration": log_data["duration"]
            },
            "time": log_data["timestamp"]
        }

        try:
            self.write_api.write(bucket=INFLUXDB_BUCKET, org=INFLUXDB_ORG, record=influx_payload, token=INFLUXDB_TOKEN)
            logging.info("Log added to InfluxDB.")
        except Exception as e:
            logging.error(f"Error adding log to InfluxDB: {e}")
