import unittest
from influxdb_client import InfluxDBClient
from storage import InfluxDBStorage
from test_base import TestBase

INFLUXDB_URL = "http://rated_db:8086"
INFLUXDB_TOKEN = "MyInitialAdminToken0=="
INFLUXDB_ORG = "rated_org"
INFLUXDB_BUCKET = "rated_http_logs_bucket"


class TestStorage(TestBase):
    def setUp(self):
        self.test_log_data = [{
            'measurement': 'api_requests',
            'tags': {'customer_id': 'cust_5', 'success': 1},
            'fields': {'duration': 0.772, 'status_code': 200, 'request_path': '/api/v1/resource4'},
            'time': '2024-09-14T16:15:35Z'},
        ]

        self.influx_client = InfluxDBClient(url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG)
        self.storage = InfluxDBStorage()

    def test_store_and_query_log(self):
        self.storage.store_log(self.test_log_data)

        customer_id = self.test_log_data[0]['tags']['customer_id']
        success = self.test_log_data[0]['tags']['success']
        duration = self.test_log_data[0]['fields']['duration']
        status_code = self.test_log_data[0]['fields']['status_code']
        request_path = self.test_log_data[0]['fields']['request_path']

        # Query the stored log data from InfluxDB
        result = self.influx_client.query_api().query(
            org=INFLUXDB_ORG,
            query=f'''
                from(bucket: "{INFLUXDB_BUCKET}")
                  |> range(start: 0)
                  |> filter(fn: (r) => r._measurement == "api_requests")
            '''
        )

        # Should be 3 tables
        self.assertEqual(len(result), 3)
        # Should 1 record in every table
        self.assertEqual(len(result[0].records), 1)
        self.assertEqual(len(result[1].records), 1)
        self.assertEqual(len(result[2].records), 1)

        # Assert the exact expected record for each table
        for table in result:
            record = table.records[0].values
            if record['_field'] == 'duration':
                self.assertEqual(record['_value'], duration)
            elif record['_field'] == 'status_code':
                self.assertEqual(record['_value'], status_code)
            elif record['_field'] == 'request_path':
                self.assertEqual(record['_value'], request_path)

            self.assertEqual(record['_measurement'], 'api_requests')
            self.assertEqual(record['customer_id'], customer_id)
            self.assertEqual(record['success'], str(success))

    def tearDown(self):
        # Clean up the InfluxDB data after the test
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
