from influxdb_client import InfluxDBClient
from log_handler import LogHandler
from storage import InfluxDBStorage
from test_influx_client import InfluxClient
from test_base import TestBase

INFLUXDB_URL = "http://rated_db:8086"
INFLUXDB_TOKEN = "MyInitialAdminToken0=="
INFLUXDB_ORG = "rated_org"
INFLUXDB_BUCKET = "rated_http_logs_bucket"


class TestCustomerStatsIntegration(TestBase):

    def setUp(self):
        self.storage = InfluxDBStorage()
        self.processor = LogHandler(self.storage)

        self.logs_cust_1 = [
            "2024-09-29 01:00:00 cust_1 /api/v1/resource 200 0.5",
            "2024-09-29 01:10:00 cust_1 /api/v1/resource 201 0.6",
            "2024-09-29 01:20:00 cust_1 /api/v1/resource 500 0.9",
            "2024-09-29 01:30:00 cust_1 /api/v1/resource 404 0.7",
            "2024-09-29 01:40:00 cust_1 /api/v1/resource 200 1.5"
        ]

        self.logs_cust_2 = [
            "2024-09-30 01:00:00 cust_2 /api/v1/resource 200 1.5",
            "2024-09-30 01:10:00 cust_2 /api/v1/resource 201 0.8",
            "2024-09-30 01:20:00 cust_2 /api/v1/resource 500 1.7",
            "2024-09-30 01:30:00 cust_2 /api/v1/resource 400 1.6"
        ]

        # process all logs, eventually they get saved in influxdb
        self.processor.handle_log(self.logs_cust_1)
        self.processor.handle_log(self.logs_cust_2)

    def test_stats_for_cust_1(self):
        stats = InfluxClient().get_stats("cust_1", "2024-09-29")

        self.assertEqual(stats["total_requests"], 5)
        self.assertEqual(stats["successful_requests"], 3)
        self.assertEqual(stats["failed_requests"], 2)
        self.assertAlmostEqual(stats["average_latency"], 0.84, places=2)
        self.assertAlmostEqual(stats["median_latency"], 0.7, places=2)
        self.assertAlmostEqual(stats["p99_latency"], 1.5, places=2)
        self.assertEqual(stats["uptime"], 60.0)

    def test_stats_for_cust_2(self):
        stats = InfluxClient().get_stats("cust_2", "2024-09-30")

        self.assertEqual(stats["total_requests"], 4)
        self.assertEqual(stats["successful_requests"], 2)
        self.assertEqual(stats["failed_requests"], 2)
        self.assertAlmostEqual(stats["average_latency"], 1.4, places=2)
        self.assertAlmostEqual(stats["median_latency"], 1.6, places=2)
        self.assertAlmostEqual(stats["p99_latency"], 1.7, places=2)
        self.assertEqual(stats["uptime"], 50.0)

    def tearDown(self):
        # nuke the db bucket ;D
        self.influx_client = InfluxDBClient(url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG)
        delete_api = self.influx_client.delete_api()
        delete_api.delete(
            start="1970-01-01T00:00:00Z",
            stop="2049-12-31T23:59:59Z",
            predicate='_measurement="api_requests"',
            bucket="rated_http_logs_bucket",
            org="rated_org"
        )
