import logging
from influxdb_client import InfluxDBClient
from config import INFLUXDB_URL, INFLUXDB_TOKEN, INFLUXDB_ORG
from storage import InfluxDBStorage
from dataflow_manager import create_dataflow

logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(levelname)s: %(message)s',
        handlers=[
            logging.FileHandler('log_processor.log'),
            logging.StreamHandler()
        ]
    )

log_file_path = "/log_generator/api_requests.log"

influx_client = InfluxDBClient(url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG, ssl=False, verify_ssl=False)
influx_storage = InfluxDBStorage(influx_client)

flow = create_dataflow(log_file_path, influx_storage)