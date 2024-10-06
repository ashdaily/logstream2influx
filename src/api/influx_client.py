import logging

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
        end_time: datetime = datetime.now()  # Today's date as the end time
        return start_time.isoformat() + "Z", end_time.isoformat() + "Z"

    def get_all_stats(self, _date: str) -> Optional[Dict[str, float]]:
        start_time, end_time = InfluxClient.get_start_end_times(_date)

        query = f'''
                from(bucket: "{self.bucket}")
                  |> range(start: {start_time}, stop: {end_time})
                  |> filter(fn: (r) => r._measurement == "api_requests")
                  |> keep(columns: ["_time", "customer_id", "success", "_field", "_value", "request_path"])
                '''

        result = self.reader_client.query(org=self.org, query=query)

        unique_records = set()
        total_success = 0
        total_failed = 0
        latencies = []

        for table in result:
            for record in table.records:
                # Create a composite key using timestamp, customer_id
                try:
                    timestamp = record.get_time()
                    customer_id = record['customer_id']
                    composite_key = (timestamp, customer_id)
                except Exception as e:
                    logging.error(f"error while creating composite key: {e}")
                else:
                    if composite_key not in unique_records:
                        unique_records.add(composite_key)

                        success_value = int(record['success'])
                        if success_value == 1:
                            total_success += 1
                        else:
                            total_failed += 1

                    if record['_field'] == 'duration' and isinstance(record["_value"], float):
                        latencies.append(record["_value"])

        # Latency calculations (mean, median, p99)
        if latencies:
            mean_latency = sum(latencies) / len(latencies)
            median_latency = sorted(latencies)[len(latencies) // 2]
            p99_latency = sorted(latencies)[int(0.99 * len(latencies))] if len(latencies) > 1 else latencies[-1]
        else:
            mean_latency = median_latency = p99_latency = None

        # Calculate total requests and uptime percentage
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

    def get_stats(self, _customer_id: str, _date: str) -> Optional[Dict[str, float]]:
        start_time, end_time = InfluxClient.get_start_end_times(_date)

        # Fetch all fields (we will filter and count based on the unique _time)
        query = f'''
        from(bucket: "{self.bucket}")
          |> range(start: {start_time}, stop: {end_time})
          |> filter(fn: (r) => r._measurement == "api_requests" and r.customer_id == "{_customer_id}")
          |> keep(columns: ["_time", "customer_id", "success", "_field", "_value"])
        '''

        result = self.reader_client.query(org=self.org, query=query)

        timestamps = set()
        total_success = 0
        total_failed = 0
        latencies = []

        for table in result:
            for record in table.records:
                # Count only once per unique timestamp
                timestamp = record.get_time()
                if timestamp not in timestamps:
                    timestamps.add(timestamp)

                    # Success or failure determination
                    if record['success'] == '1':
                        total_success += 1
                    else:
                        total_failed += 1

                # If the field is 'duration', collect it for latency calculations
                if record['_field'] == 'duration' and isinstance(record["_value"], float):
                    latencies.append(record["_value"])

        # Latency calculations (mean, median, p99)
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