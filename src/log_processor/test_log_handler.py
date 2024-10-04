import unittest
from log_handler import LogHandler
from test_base import TestBase


class MockStorage:
    def __init__(self):
        self.log_data = None

    def store_log(self, log_data):
        self.log_data = log_data


class TestLogProcessor(TestBase):
    def setUp(self):
        self.log_lines = ["2024-09-14 16:15:35 cust_5 /api/v1/resource4 200 0.772"]
        self.mock_storage = MockStorage()
        self.processor = LogHandler(self.mock_storage)

    def test_log_handler_handler_valid_logs_and_transforms_them_to_influxdb_acceptable_iterable(self):
        input_log_lines = ["2024-09-14 16:15:35 cust_5 /api/v1/resource4 200 0.772"]
        expected_ready_log_data = [{'measurement': 'api_requests', 'tags': {'customer_id': 'cust_5', 'success': 1},
                                    'fields': {'duration': 0.772,
                                               'status_code': 200, 'request_path': '/api/v1/resource4'},
                                    'time': '2024-09-14T16:15:35Z'}]

        self.processor.handle_log(input_log_lines)

        self.assertIsNotNone(self.mock_storage.log_data)
        self.assertEqual(self.mock_storage.log_data, expected_ready_log_data)

    def test_log_handler_should_convert_log_timestamp_to_influxdb_acceptable(self):
        input_log_lines = ["2024-09-15 16:15:35 cust_5 /api/v1/resource3 200 0.772"]

        self.processor.handle_log(input_log_lines)

        self.assertIsNotNone(self.mock_storage.log_data)
        self.assertEqual(self.mock_storage.log_data[0]["time"], "2024-09-15T16:15:35Z")

    def test_handle_log_line_with_error_status_code_should_be_processed_as_success_equals_0(self):
        log_lines = ["2024-09-14 16:15:35 cust_5 /api/v1/resource4 400 0.772"]
        self.processor.handle_log(log_lines)

        self.assertIsNotNone(self.mock_storage.log_data)
        self.assertEqual(self.mock_storage.log_data[0]["tags"]["success"], 0)

    def test_handle_log_line_with_http_success_code_should_be_processed_as_success_equals_1(self):
        log_lines = ["2024-09-14 16:15:35 cust_5 /api/v1/resource4 200 0.772"]

        self.processor.handle_log(log_lines)

        self.assertIsNotNone(self.mock_storage.log_data)
        self.assertEqual(self.mock_storage.log_data[0]["tags"]["success"], 1)

    def test_handle_should_transform_status_code_to_int_type(self):
        log_lines = ["2024-09-14 16:15:35 cust_5 /api/v1/resource4 200 0.772"]

        self.processor.handle_log(log_lines)

        self.assertIsNotNone(self.mock_storage.log_data)
        self.assertTrue(isinstance(self.mock_storage.log_data[0]["fields"]["status_code"], int))
        self.assertEqual(self.mock_storage.log_data[0]["fields"]["status_code"], 200)

    def test_handle_should_transform_duration_to_float_type(self):
        log_lines = ["2024-09-14 16:15:35 cust_6 /api/v1/resource4 200 0.772"]

        self.processor.handle_log(log_lines)

        self.assertIsNotNone(self.mock_storage.log_data)
        self.assertTrue(isinstance(self.mock_storage.log_data[0]["fields"]["duration"], float))
        self.assertEqual(self.mock_storage.log_data[0]["fields"]["duration"], 0.772)

    def test_handling_invalid_log_should_not_be_passed_to_storage(self):
        log_lines = ["invalid_log_format", ]

        self.processor.handle_log(log_lines)

        self.assertListEqual(self.mock_storage.log_data, [])


if __name__ == "__main__":
    unittest.main()
