import logging
from abc import ABC, abstractmethod

from influxdb_client import InfluxDBClient, WriteOptions
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
            with InfluxDBClient(url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG) as _client:
                with _client.write_api(write_options=WriteOptions(batch_size=LOG_BATCH_SIZE,
                                                                  flush_interval=10_000,
                                                                  jitter_interval=2_000,
                                                                  retry_interval=5_000,
                                                                  max_retries=5,
                                                                  max_retry_delay=30_000,
                                                                  max_close_wait=300_000,
                                                                  exponential_base=2)) as _write_client:
                    _write_client.write(INFLUXDB_BUCKET, INFLUXDB_ORG, log_data)
        except Exception as e:
            logging.error(f"Error writing log to InfluxDB: {e}")
