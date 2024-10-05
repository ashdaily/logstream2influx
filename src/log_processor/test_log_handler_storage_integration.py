import unittest
from influxdb_client import InfluxDBClient
from storage import InfluxDBStorage
from log_handler import LogHandler
from test_base import TestBase


INFLUXDB_URL = "http://rated_db:8086"
INFLUXDB_TOKEN = "MyInitialAdminToken0=="
INFLUXDB_ORG = "rated_org"
INFLUXDB_BUCKET = "rated_http_logs_bucket"


class TestCustomerStatsIntegration(TestBase):
    def setUp(self):
        self.test_log_data = [
            "2024-09-14 16:15:35 cust_1 /api/v1/resource2 200 1.234",
            "2024-09-14 16:16:35 cust_1 /api/v1/resource3 500 2.345",
            "2024-09-14 16:17:35 cust_1 /api/v1/resource4 201 0.654"
        ]

        self.influx_client = InfluxDBClient(url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG)
        self.storage = InfluxDBStorage()

        self.processor = LogHandler(self.storage)

    def test_log_handler_and_storage(self):
        self.processor.handle_log(self.test_log_data)

        query = f'''
            from(bucket: "{INFLUXDB_BUCKET}")
            |> range(start: 1970-01-01T00:00:00Z, stop: now())
            |> filter(fn: (r) => r["_measurement"] == "api_requests")
            |> filter(fn: (r) => r["customer_id"] == "cust_1")
        '''

        result = self.influx_client.query_api().query(org=INFLUXDB_ORG, query=query)

        unique_timestamps = set()
        for table in result:
            for record in table.records:
                unique_timestamps.add(record.get_time())

        self.assertEqual(len(unique_timestamps), 3)

    def test_no_logs(self):
        # No logs handled, should return an empty result
        query = f'''
            from(bucket: "{INFLUXDB_BUCKET}")
            |> range(start: 1970-01-01T00:00:00Z, stop: now())
            |> filter(fn: (r) => r["_measurement"] == "api_requests")
            |> filter(fn: (r) => r["customer_id"] == "cust_1")
        '''

        result = self.influx_client.query_api().query(org=INFLUXDB_ORG, query=query)

        unique_timestamps = set()
        for table in result:
            for record in table.records:
                unique_timestamps.add(record.get_time())

        # There should be no records
        self.assertEqual(len(unique_timestamps), 0)

    def test_logs_with_multiple_customer_id(self):
        # Insert logs for cust_1 and cust_2
        cust_1_logs = [
            "2024-09-14 16:15:35 cust_1 /api/v1/resource2 200 1.234",
            "2024-09-14 16:16:35 cust_1 /api/v1/resource3 500 2.345",
        ]
        cust_2_logs = [
            "2024-09-14 16:20:35 cust_2 /api/v1/resource2 200 1.000",
            "2024-09-14 16:21:35 cust_2 /api/v1/resource3 404 2.000",
        ]
        self.processor.handle_log(cust_1_logs)
        self.processor.handle_log(cust_2_logs)

        # Query for only cust_1 logs
        query = f'''
            from(bucket: "{INFLUXDB_BUCKET}")
            |> range(start: 1970-01-01T00:00:00Z, stop: now())
            |> filter(fn: (r) => r["_measurement"] == "api_requests")
            |> filter(fn: (r) => r["customer_id"] == "cust_1")
        '''

        result = self.influx_client.query_api().query(org=INFLUXDB_ORG, query=query)

        unique_timestamps = set()
        for table in result:
            for record in table.records:
                unique_timestamps.add(record.get_time())

        # Should only count cust_1 logs
        self.assertEqual(len(unique_timestamps), 2)

    def test_success_and_failure_logs(self):
        # Insert logs with both success and failure status codes
        log_data = [
            "2024-09-14 16:15:35 cust_1 /api/v1/resource2 200 1.234",
            "2024-09-14 16:16:35 cust_1 /api/v1/resource3 500 2.345",
            "2024-09-14 16:17:35 cust_1 /api/v1/resource4 201 0.654",
        ]
        self.processor.handle_log(log_data)

        query_success = f'''
            from(bucket: "{INFLUXDB_BUCKET}")
            |> range(start: 1970-01-01T00:00:00Z, stop: now())
            |> filter(fn: (r) => r["_measurement"] == "api_requests")
            |> filter(fn: (r) => r["customer_id"] == "cust_1")
            |> filter(fn: (r) => r["success"] == "1")
        '''

        query_failure = f'''
            from(bucket: "{INFLUXDB_BUCKET}")
            |> range(start: 1970-01-01T00:00:00Z, stop: now())
            |> filter(fn: (r) => r["_measurement"] == "api_requests")
            |> filter(fn: (r) => r["customer_id"] == "cust_1")
            |> filter(fn: (r) => r["success"] == "0")
        '''

        result_success = self.influx_client.query_api().query(org=INFLUXDB_ORG, query=query_success)
        success_timestamps = set(record.get_time() for table in result_success for record in table.records)
        self.assertEqual(len(success_timestamps), 2)

        result_failure = self.influx_client.query_api().query(org=INFLUXDB_ORG, query=query_failure)
        failure_timestamps = set(record.get_time() for table in result_failure for record in table.records)
        self.assertEqual(len(failure_timestamps), 1)

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
