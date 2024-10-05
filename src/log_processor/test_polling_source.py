import unittest
import os
import time
from polling_source import LogPollingSource
from test_base import TestBase


class TestLogPollingSource(TestBase):
    def setUp(self):
        self.log_file_path = 'test_log.log'
        with open(self.log_file_path, 'w') as f:
            f.write("2024-09-14 16:15:35 cust_5 /api/v1/resource4 200 0.772\n")
        self.source = LogPollingSource(self.log_file_path, poll_interval=1)

    def test_polling_new_line(self):
        # Simulate writing a new log line to the file
        time.sleep(2)  # Wait for the poll interval
        with open(self.log_file_path, 'a') as f:
            f.write("2024-09-14 16:16:00 cust_5 /api/v1/resource4 404 1.345\n")

        # By now LogPollingSource should detect changes
        line = self.source.next_item()
        self.assertIsNotNone(line)
        self.assertEqual(line[1], "2024-09-14 16:16:00 cust_5 /api/v1/resource4 404 1.345")

    def tearDown(self):
        self.source.close()
        if os.path.exists(self.log_file_path):
            os.remove(self.log_file_path)


if __name__ == "__main__":
    unittest.main()
