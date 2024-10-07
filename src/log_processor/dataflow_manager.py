import logging
from datetime import timedelta
import bytewax.operators as op
from bytewax.dataflow import Dataflow
from log_handler import LogHandler
from polling_source import LogPollingSource
from log_watcher import LogWatcher
from config import STREAM_MAX_SIZE, STREAM_MAX_WAIT_TIME_IN_SECONDS
import queue
import asyncio


def create_dataflow(log_file_path):
    logging.info(f"Creating dataflow for log file: {log_file_path}")
    flow = Dataflow("log_processor_flow")

    stream_queue = queue.Queue()

    log_watcher = LogWatcher(log_file_path, stream_queue)
    log_watcher.start()

    log_stream = op.input("polling_input", flow,
                          LogPollingSource(stream_queue, poll_interval=1))  # poll interval i micro seconds

    logging.info(f"stream is setup to collect {STREAM_MAX_SIZE}, with a timeout {STREAM_MAX_WAIT_TIME_IN_SECONDS}")
    collected_stream = op.collect(
        "log_processor_flow", log_stream,
        timeout=timedelta(seconds=STREAM_MAX_WAIT_TIME_IN_SECONDS), max_size=STREAM_MAX_SIZE
    )

    extracted_stream = op.map("extract_log_line", collected_stream, lambda x: x[1])

    log_handler_cls = LogHandler()

    # We need a synchronous wrapper for the async handle_log
    def sync_handle_log(log_lines):
        # Now handle_log is async and returns a coroutine
        asyncio.run(log_handler_cls.handle_log(log_lines))
    # Use log handler to process logs (wrapped in synchronous execution)
    processed_stream = op.map("process_log", extracted_stream, sync_handle_log)

    logging.info("Log processing step added to dataflow.")

    op.inspect("inspect_step", processed_stream, lambda step_id, x: logging.info(f"Inspect: {step_id}"))

    return flow
