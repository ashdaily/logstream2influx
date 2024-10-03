import unittest
from unittest.mock import patch
from fastapi.testclient import TestClient
from main import app
import logging


class TestCustomerAPI(unittest.TestCase):
    def setUp(self):
        logging.disable(logging.CRITICAL)
        self.client = TestClient(app)
        self.mock_stats_response = {
            "total_requests": 10,
            "successful_requests": 6,
            "failed_requests": 4,
            "uptime": 60.0,
            "average_latency": 0.5,
            "median_latency": 0.4,
            "p99_latency": 0.8
        }

    @patch('influx_client.InfluxClient.get_stats')
    def test_get_customer_stats_success(self, mock_get_stats):
        # valid influxdb response
        mock_get_stats.return_value = self.mock_stats_response

        response = self.client.get("/customers/cust_1/stats?from_date=2024-10-01")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), self.mock_stats_response)

    @patch('influx_client.InfluxClient.get_stats')
    def test_get_customer_stats_no_data_found(self, mock_get_stats):
        # no data found
        mock_get_stats.return_value = None

        response = self.client.get("/customers/cust_1/stats?from_date=2024-10-01")
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(), {'detail': 'Failed to retrieve stats: 404: Customer data not found'})

    @patch('influx_client.InfluxClient.get_stats')
    def test_get_customer_stats_invalid_customer_id(self, mock_get_stats):
        # response for invalid customer
        mock_get_stats.side_effect = Exception("Customer not found")

        response = self.client.get("/customers/invalid-customer-id/stats?from_date=2024-10-01")
        self.assertEqual(response.status_code, 500)

    def test_get_customer_stats_fails_on_passing_bad_date(self):
        response = self.client.get("/customers/cust_1/stats?from_date=01-01-2023")
        self.assertEqual(response.status_code, 422)

    @patch('influx_client.InfluxClient.get_stats')
    def test_get_customer_stats_future_date(self, mock_get_stats):
        mock_get_stats.return_value = self.mock_stats_response
        response = self.client.get("/customers/cust_1/stats?from_date=3024-10-01")
        self.assertEqual(response.status_code, 422)

    @patch('influx_client.InfluxClient.get_stats')
    def test_get_customer_stats_partial_data(self, mock_get_stats):
        # partial data (some fields missing)
        mock_get_stats.return_value = {
            "total_requests": 5,
            "successful_requests": 5,
            "failed_requests": 0,
            "uptime": 100.0,
            "average_latency": 0.2,
            "median_latency": None,
            "p99_latency": None
        }

        response = self.client.get("/customers/cust_1/stats?from_date=2024-10-01")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {
            "total_requests": 5,
            "successful_requests": 5,
            "failed_requests": 0,
            "uptime": 100.0,
            "average_latency": 0.2,
            "median_latency": None,
            "p99_latency": None
        })


if __name__ == '__main__':
    unittest.main()
