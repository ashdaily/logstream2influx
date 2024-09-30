import sys
from datetime import datetime, timedelta
from influxdb_client import InfluxDBClient

INFLUX_URL = "http://localhost:8086"
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

    query = f'''
    // Count successful requests (status_code starts with "2" or "3")
    success = from(bucket: "{INFLUX_BUCKET}")
      |> range(start: {start_time}, stop: {end_time})
      |> filter(fn: (r) => r._measurement == "api_requests" and r.customer_id == "{customer_id}")
      |> filter(fn: (r) => r.status_code =~ /^2/ or r.status_code =~ /^3/)
      |> count(column: "_value")
      |> yield(name: "success_count")

    // Count failed requests (status_code starts with "4" or "5")
    failed = from(bucket: "{INFLUX_BUCKET}")
      |> range(start: {start_time}, stop: {end_time})
      |> filter(fn: (r) => r._measurement == "api_requests" and r.customer_id == "{customer_id}")
      |> filter(fn: (r) => r.status_code =~ /^4/ or r.status_code =~ /^5/)
      |> count(column: "_value")
      |> yield(name: "failed_count")

    // Calculate latencies for the "duration" field
    latencies = from(bucket: "{INFLUX_BUCKET}")
      |> range(start: {start_time}, stop: {end_time})
      |> filter(fn: (r) => r._measurement == "api_requests" and r.customer_id == "{customer_id}" and r._field == "duration")
      |> group(columns: ["customer_id"])
      |> mean(column: "_value") |> yield(name: "mean_latency")
      |> median(column: "_value") |> yield(name: "median_latency")
      |> quantile(column: "_value", q: 0.99) |> yield(name: "p99_latency")
    '''

    result = query_api.query(org=INFLUX_ORG, query=query)

    stats = {
        "total_success": 0,
        "total_failed": 0,
        "mean_latency": None,
        "median_latency": None,
        "p99_latency": None,
        "uptime": None
    }

    for table in result:
        for record in table.records:
            result_type = record["result"]
            value = record["_value"]
            if result_type == "success_count":
                stats["total_success"] = value
            elif result_type == "failed_count":
                stats["total_failed"] = value
            elif result_type == "mean_latency":
                stats["mean_latency"] = value
            elif result_type == "median_latency":
                stats["median_latency"] = value
            elif result_type == "p99_latency":
                stats["p99_latency"] = value

    if stats["total_success"] + stats["total_failed"] > 0:
        stats["uptime"] = (stats["total_success"] / (stats["total_success"] + stats["total_failed"])) * 100

    client.close()
    return stats

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python customer_stats.py <customer_id> <YYYY-MM-DD>")
        sys.exit(1)

    customer_id = sys.argv[1]
    date = sys.argv[2]

    try:
        datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        print("Error: Date must be in YYYY-MM-DD format")
        sys.exit(1)

    stats = query_all_stats(customer_id, date)
    print("Customer stats:", stats)
