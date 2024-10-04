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

    def store_log(self, log_data):
        try:
            with InfluxDBClient(url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG) as _client:

                with _client.write_api(write_options=WriteOptions(batch_size=LOG_BATCH_SIZE*100,
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
        finally:
            logging.info(f"Influx Db object count now: {InfluxDBStorage.count_total_logs()}")

    @staticmethod
    def count_total_logs() -> int:
        query = f'''
        from(bucket: "{INFLUXDB_BUCKET}")
          |> range(start: 0)
          |> filter(fn: (r) => r._measurement == "api_requests")
          |> count(column: "_value")
        '''

        result = InfluxDBClient(url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG).query_api()\
            .query(org=INFLUXDB_ORG, query=query)
        total_count = 0
        for table in result:
            for record in table.records:
                total_count += record["_value"]
        return total_count

    # def query_log_data(self, log_data: dict):
    #     try:
    #         self.write_api.write(
    #             bucket=INFLUXDB_BUCKET,
    #             org=INFLUXDB_ORG,
    #             record=log_data,
    #         )
    #     except Exception as e:
    #         logging.error(f"Failed to write log to InfluxDB: {e}")
