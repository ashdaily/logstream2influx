import logging

from influxdb_client.client.write_api import SYNCHRONOUS
from datetime import datetime
from typing import Dict, Tuple, Optional

from config import INFLUXDB_TOKEN, INFLUXDB_BUCKET, INFLUXDB_ORG, INFLUXDB_URL
from influxdb_client import InfluxDBClient


class InfluxClient:
    PRECISION = 5

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
        end_time: datetime = datetime.now()  # Today's date as the end time
        return start_time.isoformat() + "Z", end_time.isoformat() + "Z"

    def get_all_stats(self, _date: str) -> Optional[Dict[str, float]]:
        start_time, end_time = InfluxClient.get_start_end_times(_date)

        query = """
                from(bucket: "{bucket}")
                  |> range(start: {start_time}, stop: {end_time})
                  |> filter(fn: (r) => r._measurement == "api_requests")
                """.format(bucket=self.bucket, start_time=start_time, end_time=end_time)

        result = self.reader_client.query(org=self.org, query=query)

        return self._calculate(result)

    def get_stats(self, _customer_id: str, _date: str) -> Optional[Dict[str, float]]:
        start_time, end_time = InfluxClient.get_start_end_times(_date)
        query = """
                from(bucket: "{bucket}")
                  |> range(start: {start_time}, stop: {end_time})
                  |> filter(fn: (r) => r._measurement == "api_requests" and r.customer_id == "{customer_id}")
                  |> keep(columns: ["_time", "customer_id", "success", "_field", "_value"])
                """.format(bucket=self.bucket, start_time=start_time, end_time=end_time, customer_id=_customer_id)

        result = self.reader_client.query(org=self.org, query=query)
        return self._calculate(result)

    def _calculate(self, _result) -> Optional[Dict[str, float]]:
        try:
            stats = {}
            for table in _result:
                for record in table.records:
                    metric = record.values.get("_field")
                    value = record.values.get("_value")
                    if stats.get(metric):
                        stats[metric].append(value)
                    else:
                        stats[metric] = [value]

            # Process total requests, success, and failed
            for i, v in stats.items():
                logging.info(f"{i}: {len(v)}")
            total_requests = stats.get("total_requests", max([len(s) for s in stats.values()]))
            total_success = stats.get("total_success", sum([1 if s < 400 else 0 for s in stats["status_code"]]))
            total_failed = stats.get("total_failed", sum([1 if s >= 400 else 0 for s in stats["status_code"]]))

            # Calculate average, median, and p99 latency
            latencies = stats.get("duration", [])

            if latencies:
                latencies = sorted(latencies)
                average_latency = sum(latencies) / len(latencies) if latencies else None
                median_latency = latencies[len(latencies) // 2] if latencies else None
                p99_latency = latencies[int(len(latencies) * 0.99) - 1] if len(latencies) >= 100 else latencies[-1]
            else:
                average_latency, median_latency, p99_latency = None, None, None

            return {
                "total_requests": total_requests,
                "successful_requests": total_success,
                "failed_requests": total_failed,
                "uptime": round((total_success / total_requests) * 100, self.PRECISION) if total_requests else 0,
                "average_latency": round(average_latency, self.PRECISION),
                "median_latency": round(median_latency, self.PRECISION),
                "p99_latency": round(p99_latency, self.PRECISION)
            }
        except Exception as e:
            logging.error(f"Error while retrieving stats for all customers: {e}")
            return None
