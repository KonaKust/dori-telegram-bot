import os
import time
import redis
import socket
import json
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from loguru import logger


class LogFileWatcher:
    def __init__(
        self,
        redis_key: str,
        log_file_path: str,
        file_name: str,
        target_words: list,
        ignored_words: list,
    ):
        self.redis_key = redis_key
        self.log_file_path = log_file_path
        self.file_name = file_name
        self.target_words = target_words
        self.ignored_words = ignored_words
        self.log_file = os.path.join(log_file_path, self.file_name)
        self.setup_redis()

        logger.info(f"Tracking {self.log_file}")

    def setup_redis(self):
        self.redis = redis.Redis(host="localhost", port=6379, decode_responses=True)
        if not self.redis.exists(self.redis_key):
            self.redis.set(self.redis_key, 1)

    def check_log_file(self, start_position):
        current_position = start_position
        first_line_with_target_word = None

        with open(self.log_file, "r") as file:
            for line_number, line in enumerate(file, 1):
                if line_number < current_position:
                    continue
                if not line:
                    return None, None

                ignore_line = any(word in line for word in self.ignored_words)
                if ignore_line:
                    current_position = line_number + 1
                    logger.info(f"Ignore line {line_number}")
                    continue

                word_found = any(word in line for word in self.target_words)
                if word_found:
                    first_line_with_target_word = line.strip()
                    current_position = line_number + 1
                    break

        return current_position, first_line_with_target_word

    def send_notification(self, data):
        host = "127.0.0.1"
        port = 8888

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            client_socket.connect((host, port))
            encoded_data = json.dumps(data).encode()
            client_socket.sendall(encoded_data)

    def start_observer(self):
        event_handler = LogFileHandler(
            self.redis,
            self.redis_key,
            self.check_log_file,
            self.send_notification,
            self.log_file,
        )
        observer = Observer()
        observer.schedule(event_handler, path=self.log_file_path, recursive=False)

        try:
            observer.start()
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
        observer.join()


class LogFileHandler(FileSystemEventHandler):
    def __init__(self, redis, redis_key, check_log_file, send_notification, log_file):
        super().__init__()
        self.redis = redis
        self.redis_key = redis_key
        self.check_log_file = check_log_file
        self.send_notification = send_notification
        self.log_file = log_file

    def on_modified(self, event):
        if event.src_path == self.log_file:
            while True:
                current_position = int(self.redis.get(self.redis_key))
                result = self.check_log_file(current_position)
                if result[1] is not None:
                    data = {"factorio": result[1]}
                    self.send_notification(data)
                    # logger.info(f"{result[0]}: {data}")
                    self.redis.set(self.redis_key, value=result[0])
                else:
                    break
