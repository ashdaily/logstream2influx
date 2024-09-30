import logging
import bytewax.operators as op
from bytewax.dataflow import Dataflow
from bytewax.connectors.stdio import StdOutSink
from polling_source import LogPollingSource
from storage import InfluxDBStorage
from log_handler import LogProcessor


def create_dataflow(log_file_path, influx_storage):
    logging.info(f"Creating dataflow for log file: {log_file_path}")
    flow = Dataflow("log_processor_flow")

    # Poll the log file for new entries every 5 seconds
    log_stream = op.input("polling_input", flow, LogPollingSource(log_file_path, 5))
    logging.info("Log polling source created.")

    # Extract the log line (the second element of the tuple)
    extracted_log_stream = op.map("extract_log_line", log_stream, lambda x: x[1])
    logging.info("Log extraction step added to dataflow.")

    # Process each log entry using the LogProcessor
    log_processor = LogProcessor(influx_storage)
    processed_stream = op.map("process_log", extracted_log_stream, log_processor.handle_log)
    logging.info("Log processing step added to dataflow.")

    # Output to StdOut (for debugging)
    op.output("stdout_output", processed_stream, StdOutSink())
    logging.info("Output step added to dataflow.")

    return flow
