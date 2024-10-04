import unittest
from datetime import datetime
from influxdb_client import InfluxDBClient
from storage import InfluxDBStorage


INFLUXDB_URL = "http://rated_db:8086"
INFLUXDB_TOKEN = "MyInitialAdminToken0=="
INFLUXDB_ORG = "rated_org"
INFLUXDB_BUCKET = "rated_http_logs_bucket"


class TestInfluxDBStorageIntegration(unittest.TestCase):
    def setUp(self):
        self.test_log_data = {
            "timestamp": datetime.now().isoformat() + "Z",
            "customer_id": "cust_1",
            "request_path": "/api/v1/resource2",
            "status_code": 200,
            "duration": 1.234,
            "success": 1
        }

        self.influx_client = InfluxDBClient(url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG)
        self.storage = InfluxDBStorage()

    def test_store_and_query_log(self):
        # we want to test that the log data gets stored in influxdb as we want, so we want to test against actual db
        self.storage.store_log(self.test_log_data)

        result = self.influx_client.query_api().query(
            org=INFLUXDB_ORG,
            query=f'''
                from(bucket: "{INFLUXDB_BUCKET}")
                  |> range(start: -1h)
                  |> filter(fn: (r) => r["_measurement"] == "api_requests")
                  |> filter(fn: (r) => r["customer_id"] == "{self.test_log_data['customer_id']}")
                  |> filter(fn: (r) => r["_field"] == "duration" and r["_value"] == {self.test_log_data['duration']})
                  |> filter(fn: (r) => r["success"] == "{self.test_log_data['success']}")
            '''
        )

        records = []
        for table in result:
            for record in table.records:
                records.append(record.values)

        self.assertEqual(len(records), 1, f"Expected 1 record, but found {len(records)}")

        expected_record = {
            'customer_id': self.test_log_data['customer_id'],
            'request_path': self.test_log_data['request_path'],
            'status_code': str(self.test_log_data['status_code']),  # Stored as string
            'duration': self.test_log_data['duration'],  # Stored in _value
            'success': str(self.test_log_data['success']),  # Stored as string
            '_measurement': 'api_requests',
        }

        actual_record = records[0]

        # Check all fields except duration since it's stored in _value
        for key, expected_value in expected_record.items():
            if key != 'duration':
                self.assertEqual(actual_record.get(key), expected_value)

        # Check duration which is stored in _value
        self.assertEqual(actual_record.get('_value'), expected_record['duration'])

    def tearDown(self):
        # nuke the influx db data ;)
        try:
            delete_api = self.influx_client.delete_api()
            start_time = "1970-01-01T00:00:00Z"  # epoch start time

            delete_api.delete(
                start=start_time,
                stop="2049-12-31T23:59:59Z",  # Future date far in the future to delete all data
                predicate='_measurement="api_requests"',
                bucket=INFLUXDB_BUCKET,
                org=INFLUXDB_ORG
            )
        except Exception as e:
            print(f"Error during data cleanup: {e}")


if __name__ == "__main__":
    unittest.main()
