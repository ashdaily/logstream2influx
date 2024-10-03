from influxdb_client.client.write_api import SYNCHRONOUS
from datetime import datetime, timedelta
from typing import Dict, Tuple, Optional

from config import INFLUXDB_TOKEN, INFLUXDB_BUCKET, INFLUXDB_ORG, INFLUXDB_URL
from influxdb_client import InfluxDBClient


class InfluxClient:
    def __init__(self) -> None:
        self.bucket: str = INFLUXDB_BUCKET
        self.org: str = INFLUXDB_ORG
        self.url: str = INFLUXDB_URL
        self.token: str = INFLUXDB_TOKEN
        self._client: Optional[InfluxDBClient] = None

    def __enter__(self):
        self._client = InfluxDBClient(url=self.url, token=self.token, org=self.org)
        self.reader_client = self._client.query_api()
        self.writer_client = self._client.write_api(write_options=SYNCHRONOUS)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._client:
            self._client.close()

    @staticmethod
    def get_start_end_times(_date: str) -> Tuple[str, str]:
        start_time: datetime = datetime.strptime(_date, "%Y-%m-%d")
        end_time: datetime = datetime.utcnow()  # Today's date as the end time
        return start_time.isoformat() + "Z", end_time.isoformat() + "Z"

    def get_stats(self, _customer_id: str, _date: str) -> Optional[Dict[str, float]]:
        start_time, end_time = InfluxClient.get_start_end_times(_date)

        # Fetch successful requests (2xx/3xx status codes)
        success_query = f'''
        from(bucket: "{self.bucket}")
          |> range(start: {start_time}, stop: {end_time})
          |> filter(fn: (r) => r._measurement == "api_requests" and r.customer_id == "{_customer_id}")
          |> filter(fn: (r) => r.success == "1")
        '''

        # Fetch failed requests (non-2xx/3xx status codes)
        failed_query = f'''
        from(bucket: "{self.bucket}")
          |> range(start: {start_time}, stop: {end_time})
          |> filter(fn: (r) => r._measurement == "api_requests" and r.customer_id == "{_customer_id}")
          |> filter(fn: (r) => r.success == "0")
        '''

        # Fetch latency data
        latency_query = f'''
        from(bucket: "{self.bucket}")
          |> range(start: {start_time}, stop: {end_time})
          |> filter(fn: (r) => r._measurement == "api_requests" and r.customer_id == "{_customer_id}" and r._field == "duration")
          |> group(columns: ["customer_id"])
          |> keep(columns: ["_value"])
        '''

        # Count successful requests
        success_result = self.reader_client.query(org=self.org, query=success_query)
        total_success = sum([1 for table in success_result for _ in table.records])

        # Count failed requests
        failed_result = self.reader_client.query(org=self.org, query=failed_query)
        total_failed = sum([1 for table in failed_result for _ in table.records])

        # Latency calculations (mean, median, p99)
        latency_result = self.reader_client.query(org=self.org, query=latency_query)
        latencies = [record["_value"] for table in latency_result for record in table.records]

        if latencies:
            mean_latency = sum(latencies) / len(latencies)
            median_latency = sorted(latencies)[len(latencies) // 2]
            p99_latency = sorted(latencies)[int(0.99 * len(latencies))] if len(latencies) > 1 else latencies[-1]
        else:
            mean_latency = median_latency = p99_latency = None

        total_requests = total_success + total_failed
        uptime = (total_success / total_requests) * 100 if total_requests > 0 else 0

        return {
            "total_requests": total_requests or 0,
            "successful_requests": total_success or 0,
            "failed_requests": total_failed or 0,
            "uptime": round(uptime, 5),
            "average_latency": mean_latency if mean_latency else None,
            "median_latency": median_latency if median_latency else None,
            "p99_latency": p99_latency if p99_latency else None
        }
