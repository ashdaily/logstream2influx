import logging
import os
from bytewax.inputs import SimplePollingSource
from datetime import timedelta


class LogPollingSource(SimplePollingSource):
    def __init__(self, log_file_path, poll_interval):
        logging.info(f"Initializing LogPollingSource with log file: {log_file_path} and interval: {poll_interval}s")
        self.log_file_path = log_file_path
        self.log_file = open(log_file_path, 'r')
        self.log_file.seek(0, os.SEEK_END)  # Move to the end of file
        logging.info(f"Opened log file: {log_file_path}, starting at the end.")

        super().__init__(timedelta(seconds=poll_interval))

    def next_item(self):
        line = self.log_file.readline().strip()
        if line:
            return ("ALL", line)
        return None

    def close(self):
        logging.info(f"Closing log file: {self.log_file_path}")
        self.log_file.close()
