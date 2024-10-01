import sys
from datetime import datetime, timedelta
from influxdb_client import InfluxDBClient

INFLUX_URL = "http://rated_db:8086"
INFLUX_TOKEN = "MyInitialAdminToken0=="
INFLUX_ORG = "rated_org"
INFLUX_BUCKET = "rated_http_logs_bucket"

def get_start_end_times(date_str):
    start_time = datetime.strptime(date_str, "%Y-%m-%d")
    end_time = start_time + timedelta(days=1) - timedelta(seconds=1)
    return start_time.isoformat() + "Z", end_time.isoformat() + "Z"

def query_all_stats(customer_id, date):
    client = InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG)
    query_api = client.query_api()

    start_time, end_time = get_start_end_times(date)

    # Fetch successful requests (2xx status codes)
    success_query = f'''
    from(bucket: "{INFLUX_BUCKET}")
      |> range(start: {start_time}, stop: {end_time})
      |> filter(fn: (r) => r._measurement == "api_requests" and r.customer_id == "{customer_id}")
      |> filter(fn: (r) => r.success == "1")
    '''

    # Fetch failed requests (non-2xx/3xx status codes)
    failed_query = f'''
    from(bucket: "{INFLUX_BUCKET}")
      |> range(start: {start_time}, stop: {end_time})
      |> filter(fn: (r) => r._measurement == "api_requests" and r.customer_id == "{customer_id}")
      |> filter(fn: (r) => r.success == "0")
    '''

    # Fetch latency data
    latency_query = f'''
    from(bucket: "{INFLUX_BUCKET}")
      |> range(start: {start_time}, stop: {end_time})
      |> filter(fn: (r) => r._measurement == "api_requests" and r.customer_id == "{customer_id}" and r._field == "duration")
      |> group(columns: ["customer_id"])
      |> keep(columns: ["_value"])
    '''

    # Count successful requests
    success_result = query_api.query(org=INFLUX_ORG, query=success_query)
    total_success = sum([1 for table in success_result for record in table.records])

    # Count failed requests
    failed_result = query_api.query(org=INFLUX_ORG, query=failed_query)
    total_failed = sum([1 for table in failed_result for record in table.records])

    # Latency calculations (mean, median, p99)
    latency_result = query_api.query(org=INFLUX_ORG, query=latency_query)
    latencies = [record["_value"] for table in latency_result for record in table.records]

    if latencies:
        mean_latency = sum(latencies) / len(latencies)
        median_latency = sorted(latencies)[len(latencies) // 2]
        p99_latency = sorted(latencies)[int(0.99 * len(latencies))] if len(latencies) > 1 else latencies[-1]
    else:
        mean_latency = median_latency = p99_latency = None

    # Uptime calculation
    total_requests = total_success + total_failed
    uptime = (total_success / total_requests) * 100 if total_requests > 0 else 0

    client.close()

    return {
        "total_success": total_success,
        "total_failed": total_failed,
        "mean_latency": mean_latency,
        "median_latency": median_latency,
        "p99_latency": p99_latency,
        "uptime": round(uptime, 5)
    }

