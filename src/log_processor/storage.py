import logging
from abc import ABC, abstractmethod

from influxdb_client import InfluxDBClient, WriteOptions
from influxdb_client.client.write_api import SYNCHRONOUS
from config import (
    INFLUXDB_BUCKET,
    INFLUXDB_ORG,
    INFLUXDB_URL,
    INFLUXDB_TOKEN,
    LOG_BATCH_SIZE,
)


class LogStorage(ABC):
    @abstractmethod
    def store_log(self, log_data):
        pass


class InfluxDBStorage(LogStorage):
    def __init__(self):
        pass

    def __repr__(self):
        return f"{self.__class__.__name__}"

    def store_log(self, log_data) -> None:
        if not log_data:
            logging.info(f"{self}.{self.__class__.store_log.__name__} was passed empty log_data.")
            return

        try:
            logging.info(f"InfluxDBClient writing: {len(log_data)} records")
            with InfluxDBClient(url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG) \
                .write_api(write_options=WriteOptions(
                    batch_size=500,
                    flush_interval=1000,
                    jitter_interval=500,
                    retry_interval=5000),
                    success_callback=self.success_cb, error_callback=self.error_cb, retry_callback=self.retry_cb
            ) as _client:
                _client.write(INFLUXDB_BUCKET, INFLUXDB_ORG, log_data)
                _client.__del__()
        except Exception as e:
            logging.error(f"Error writing log to InfluxDB: {e}")

    def success_cb(self, details, data):
        data = data.decode('utf-8').split('\n')
        logging.info(f"Total Rows Inserted: {len(data)}")

    def error_cb(self, details, data, exception):
        logging.error(f"Influxdb error callback: details: {details}, exception: {exception}")

    def retry_cb(self, details, data, exception):
        logging.info('Influx db retry exception:', exception)
