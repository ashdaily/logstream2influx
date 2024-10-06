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

    async def initialize(self):
        self.client = InfluxDBClientAsync(url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG)

    async def store_log(self, log_data) -> None:
        if not log_data:
            logging.info("No log data to store.")
            return

        try:
            write_api = self.client.write_api()
            batch_size = LOG_BATCH_SIZE

            # Split log_data into batches and write each batch
            for i in range(0, len(log_data), batch_size):
                batch = log_data[i:i + batch_size]
                await write_api.write(bucket=INFLUXDB_BUCKET, org=INFLUXDB_ORG, record=batch)
                logging.info(f"Successfully wrote {len(batch)} logs to InfluxDB.")
        except Exception as e:
            logging.error(f"Error writing log to InfluxDB: {e}")

    async def close(self):
        if self.client:
            await self.client.__aexit__(None, None, None)
