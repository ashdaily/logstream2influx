import logging
from datetime import timedelta

import bytewax.operators as op
from bytewax.dataflow import Dataflow
from polling_source import LogPollingSource
from log_handler import LogHandler
from config import STREAM_MAX_SIZE, STREAM_MAX_WAIT_TIME_IN_SECONDS


def create_dataflow(log_file_path, influx_storage):
    logging.info(f"Creating dataflow for log file: {log_file_path}")
    flow = Dataflow("log_processor_flow")

    log_stream = op.input("polling_input", flow, LogPollingSource(log_file_path, poll_interval=.001))

    logging.info(f"stream is setup to collect {STREAM_MAX_SIZE}, with a timeout {STREAM_MAX_WAIT_TIME_IN_SECONDS}")
    collected_stream = op.collect(
        "log_processor_flow", log_stream,
        timeout=timedelta(seconds=STREAM_MAX_WAIT_TIME_IN_SECONDS), max_size=STREAM_MAX_SIZE
    )

    extracted_stream = op.map("extract_log_line", collected_stream, lambda x: x[1])

    log_processor = LogHandler(influx_storage)
    processed_stream = op.map("process_log", extracted_stream, log_processor.handle_log)
    logging.info("Log processing step added to dataflow.")

    op.inspect("inspect_step", processed_stream, lambda step_id, x: None)
    logging.info("Inspect step added to dataflow.")

    return flow
