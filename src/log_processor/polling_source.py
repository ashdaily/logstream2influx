import logging
from bytewax.inputs import SimplePollingSource
from datetime import timedelta
import queue


class LogPollingSource(SimplePollingSource):
    def __init__(self, stream_queue, poll_interval):
        logging.debug(f"Initializing LogPollingSource with queue and interval: {poll_interval}s")
        self.stream_queue = stream_queue
        super().__init__(timedelta(microseconds=poll_interval))

    def next_item(self):
        try:
            # Try to get an item from the queue with a non-blocking call
            log_item = self.stream_queue.get_nowait()
            logging.debug(f"Pulled log item from queue: {log_item}")
            return log_item
        except queue.Empty:
            logging.debug("Queue is empty, no new logs to process.")
            return None

