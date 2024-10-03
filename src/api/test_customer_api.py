import unittest
from fastapi.testclient import TestClient
from main import app
import logging


class TestCustomerAPI(unittest.TestCase):
    def setUp(self):
        logging.disable(logging.CRITICAL)
        self.client = TestClient(app)

    def test_get_customer_stats_success(self):
        # 2024-10-01 20:58:21 cust_1 /api/v1/resource4 400 0.195
        response = self.client.get("/customers/cust_1/stats?from_date=2024-10-01")
        self.assertEqual(response.status_code, 200)

    def test_get_customer_stats_fails_on_passing_bad_date(self):
        response = self.client.get("/customers/test-customer-id/stats?from_date=01-01-2023")
        self.assertEqual(response.status_code, 422)


if __name__ == '__main__':
    unittest.main()
