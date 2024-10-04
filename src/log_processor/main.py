import logging

from config import (
    LOG_FILE_PATH,
    LOGGING_LEVEL
)
from storage import InfluxDBStorage
from dataflow_manager import create_dataflow


logging.basicConfig(
    level=getattr(logging, LOGGING_LEVEL, logging.INFO),
    format='%(asctime)s %(levelname)s: %(message)s',
    handlers=[
        logging.FileHandler('log_processor.log'),
        logging.StreamHandler()
    ]
)

influx_storage = InfluxDBStorage()


flow = create_dataflow(f"/log_generator/{LOG_FILE_PATH}", influx_storage)
