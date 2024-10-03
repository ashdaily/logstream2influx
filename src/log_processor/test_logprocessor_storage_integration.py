import unittest
import os
import tempfile
from datetime import datetime
from influxdb_client import InfluxDBClient
from storage import InfluxDBStorage
from log_handler import LogHandler


INFLUXDB_URL = "http://rated_db:8086"
INFLUXDB_TOKEN = "MyInitialAdminToken0=="
INFLUXDB_ORG = "rated_org"
INFLUXDB_BUCKET = "rated_http_logs_bucket"


class TestCustomerStatsIntegration(unittest.TestCase):
    def setUp(self):
        self.test_log_data = [
            "2024-09-14 16:15:35 cust_1 /api/v1/resource2 200 1.234",
            "2024-09-14 16:16:35 cust_1 /api/v1/resource3 500 2.345",
            "2024-09-14 16:17:35 cust_1 /api/v1/resource4 201 0.654"
        ]

        self.influx_client = InfluxDBClient(url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG)
        self.storage = InfluxDBStorage(self.influx_client)

        self.processor = LogHandler(self.storage)

    def test_log_handler_and_storage(self):
        for log_line in self.test_log_data:
            self.processor.handle_log(log_line)

        query = f'''
            from(bucket: "{INFLUXDB_BUCKET}")
            |> range(start: 1970-01-01T00:00:00Z, stop: now())
            |> filter(fn: (r) => r["_measurement"] == "api_requests")
            |> filter(fn: (r) => r["customer_id"] == "cust_1")
        '''

        result = self.storage.query_api.query(org=INFLUXDB_ORG, query=query)

        records = []
        for table in result:
            for record in table.records:
                records.append(record.values)

        self.assertEqual(len(records), 3)

    def tearDown(self):
        try:
            delete_api = self.influx_client.delete_api()
            delete_api.delete(
                start="1970-01-01T00:00:00Z",
                stop="2049-12-31T23:59:59Z",
                predicate='_measurement="api_requests"',
                bucket=INFLUXDB_BUCKET,
                org=INFLUXDB_ORG
            )
        except Exception as e:
            print(f"Error during data cleanup: {e}")


if __name__ == "__main__":
    unittest.main()
