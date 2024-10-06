import logging
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import threading


class LogWatcher(FileSystemEventHandler):
    def __init__(self, log_file_path, stream_queue):
        self.log_file_path = log_file_path
        self.log_file = open(log_file_path, 'r')
        self.log_file.seek(0, os.SEEK_END)
        self.stream_queue = stream_queue
        logging.debug(f"LogWatcher initialized with log file at: {os.path.abspath(self.log_file_path)}")

        # Watchdog observer
        self.observer = Observer()
        self.observer.schedule(self, path=log_file_path, recursive=False)

    def start(self):
        logging.debug("Starting LogWatcher observer thread.")
        observer_thread = threading.Thread(target=self.observer.start)
        observer_thread.daemon = True
        observer_thread.start()

    def stop(self):
        logging.debug("Stopping LogWatcher observer.")
        self.observer.stop()
        self.observer.join()
        self.log_file.close()

    def on_modified(self, event):
        if event.src_path == self.log_file_path:
            logging.debug(f"File modified: {self.log_file_path}")
            self._process_new_logs()

    def _process_new_logs(self):
        logging.debug("Processing new logs...")
        while line := self.log_file.readline().strip():
            logging.debug(f"New log line added to queue: {line}")
            self.stream_queue.put(("ALL", line))
        logging.debug("Finished processing new logs.")
