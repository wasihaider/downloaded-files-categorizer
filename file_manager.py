import os
import json
import logging
import shutil

import watchdog.events
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

logging_file = "/tmp/file_manager.log"
logging.basicConfig(
    filename=logging_file,
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

with open("categories.json", "r") as file:
    categories = json.load(file)
src_dir_path = os.path.expanduser("~") + "/Downloads"


def move_file(src_path):
    try:
        file_ext = src_path.split(".")[-1]
        category = categories.get(file_ext)
        if category:
            dest_dir = src_dir_path + f"/{category}"
            if not os.path.exists(dest_dir):
                os.makedirs(dest_dir)
            dest_path = dest_dir + "/" + src_path.split("/")[-1]
            shutil.move(src_path, dest_path)
            logging.info(f"file moved from {src_path} to {dest_path}")
    except Exception as e:
        logging.exception(e.__traceback__)


class MoverHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if isinstance(event, watchdog.events.FileModifiedEvent):
            logging.info(f"Found a file modified event: {event.src_path = }")

            move_file(event.src_path)


class DownloadFileManager:
    def __init__(self, src_dir):
        self.path = src_dir
        self.event_handler = MoverHandler()
        self.observer = Observer()

    def run(self):
        self.observer.schedule(self.event_handler, self.path, recursive=True)
        self.observer.start()
        try:
            while self.observer.is_alive():
                self.observer.join(1)
        finally:
            self.observer.stop()
            self.observer.join()


if __name__ == '__main__':
    logging.info("File manager is active!")
    manager = DownloadFileManager(src_dir_path)
    manager.run()
