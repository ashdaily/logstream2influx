from abc import ABC, abstractmethod
import logging
from influxdb_client.client.influxdb_client_async import InfluxDBClientAsync
from config import INFLUXDB_BUCKET, INFLUXDB_ORG, INFLUXDB_URL, INFLUXDB_TOKEN, LOG_BATCH_SIZE


class LogStorage(ABC):
    @abstractmethod
    async def store_log(self, log_data):
        pass


class InfluxDBStorage(LogStorage):
    def __init__(self):
        self.client = None
        self.write_api = None
        self.log_batch = []
        self.batch_size = 50_000 #TODO: pass from env vars

    async def initialize(self):
        self.client = InfluxDBClientAsync(url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG)
        self.write_api = self.client.write_api()

    async def store_log(self, log_data) -> None:
        if not log_data:
            logging.info("No log data to store.")
            return

        self.log_batch.extend(log_data)

        if len(self.log_batch) >= self.batch_size:
            await self.flush_logs()

    async def flush_logs(self) -> None:
        try:
            await self.write_api.write(bucket=INFLUXDB_BUCKET, org=INFLUXDB_ORG, record=self.log_batch)
            logging.info(f"Successfully wrote {len(self.log_batch)} logs to InfluxDB.")
            self.log_batch.clear()
        except Exception as e:
            logging.error(f"Error writing log to InfluxDB: {e}")

    async def close(self):
        if self.log_batch:
            await self.flush_logs()
        if self.client:
            await self.client.__aexit__(None, None, None)