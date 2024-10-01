from datetime import datetime, timedelta

from influxdb_client import InfluxDBClient
from influxdb_client.client.write_api import SYNCHRONOUS

from abc import ABC, abstractmethod
import logging
from config import INFLUXDB_BUCKET, INFLUXDB_ORG


class LogStorage(ABC):
    @abstractmethod
    def store_log(self, log_data: dict):
        pass


class InfluxDBStorage(LogStorage):
    def __init__(self, influx_client: InfluxDBClient):
        self.influx_client = influx_client
        self.query_api = self.influx_client.query_api()
        logging.info(f"InfluxDB storage initialized with bucket: {INFLUXDB_BUCKET} and org: {INFLUXDB_ORG}")

    def store_log(self, log_data: dict):
        if not isinstance(log_data, dict):
            logging.error(f"Invalid log data structure: {log_data}")
            return

        try:
            influx_payload = {
                "measurement": "api_requests",
                "tags": {
                    "customer_id": log_data["customer_id"],
                    "request_path": log_data["request_path"],
                    "status_code": log_data["status_code"],
                },
                "fields": {
                    "duration": log_data["duration"]
                },
                "time": log_data["timestamp"]
            }
            write_api = self.influx_client.write_api(write_options=SYNCHRONOUS)
            write_api.write(bucket=INFLUXDB_BUCKET, org=INFLUXDB_ORG, record=influx_payload)
        except Exception as e:
            logging.error(f"Error writing log to InfluxDB: {e}")
        else:
            self.query_log_data(log_data)

    def query_log_data(self, log_data):
        # NOTE: should not be used in prod
        try:
            log_time = datetime.fromisoformat(log_data['timestamp'].replace("Z", ""))

            # 5-second buffer around the log timestamp should help spot what we added
            start_time = (log_time - timedelta(seconds=5)).isoformat() + "Z"
            stop_time = (log_time + timedelta(seconds=5)).isoformat() + "Z"

            logging.info(f"Querying between start: {start_time} and stop: {stop_time}")

            query = f'''
            from(bucket: "{INFLUXDB_BUCKET}")
              |> range(start: {start_time}, stop: {stop_time})
              |> filter(fn: (r) => r["_measurement"] == "api_requests")
              |> filter(fn: (r) => r["customer_id"] == "{log_data['customer_id']}")
              |> filter(fn: (r) => r["request_path"] == "{log_data['request_path']}")
              |> filter(fn: (r) => r["status_code"] == "{log_data['status_code']}")
              |> filter(fn: (r) => r["_field"] == "duration" and r["_value"] == {log_data['duration']})
            '''
            result = self.query_api.query(org=INFLUXDB_ORG, query=query)

            if result:
                logging.info("Query successful. Log data stored in InfluxDB:")

                for table in result:
                    for record in table.records:
                        logging.info(f"Record: {record.values}")

            else:
                logging.warning("No exact match found for the added log data.")
        except Exception as e:
            logging.error(f"Error querying log data from InfluxDB: {e}")
