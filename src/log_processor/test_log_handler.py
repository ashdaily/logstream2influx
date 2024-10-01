import unittest
from log_handler import LogProcessor

class MockStorage:
    def __init__(self):
        self.log_data = None

    def store_log(self, log_data):
        self.log_data = log_data

class TestLogProcessor(unittest.TestCase):
    def setUp(self):
        self.mock_storage = MockStorage()
        self.processor = LogProcessor(self.mock_storage)

    def test_handle_valid_log(self):
        log_line = "2024-09-14 16:15:35 cust_5 /api/v1/resource4 200 0.772"
        self.processor.handle_log(log_line)
        self.assertIsNotNone(self.mock_storage.log_data)
        self.assertEqual(self.mock_storage.log_data["customer_id"], "cust_5")
        self.assertEqual(self.mock_storage.log_data["status_code"], 200)
        self.assertEqual(self.mock_storage.log_data["success"], 1)

    def test_handle_invalid_log(self):
        log_line = "invalid_log_format"
        self.processor.handle_log(log_line)
        self.assertIsNone(self.mock_storage.log_data)

if __name__ == "__main__":
    unittest.main()
