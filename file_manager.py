import os
import json
import logging
import shutil
import time

import PyQt5.QtWidgets as qtw
import PyQt5.QtGui as qtg
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


class FileManagerWindow(qtw.QTabWidget):
    def __init__(self, path):
        super().__init__()
        self.file_path = path

        self.setWindowTitle("Download File Manager")
        qr = self.frameGeometry()
        cp = qtw.QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())
        self.setLayout(qtw.QVBoxLayout())

        self.label = qtw.QLabel("What should be the file name?")
        self.label.setFont(qtg.QFont("Helvetica", 18))
        self.layout().addWidget(self.label)

        self.name_entry = qtw.QLineEdit()
        self.name_entry.setObjectName("filename_field")
        self.name_entry.setText(self.file_path)
        self.layout().addWidget(self.name_entry)

        self.ignore_btn = qtw.QPushButton("Ignore", self)
        self.ignore_btn.clicked.connect(self.ignore)
        self.layout().addWidget(self.ignore_btn)

        self.rename_btn = qtw.QPushButton("Rename", self)
        self.rename_btn.clicked.connect(self.rename)
        self.layout().addWidget(self.rename_btn)

        self.cat_btn = qtw.QPushButton("Categorize", self)
        self.cat_btn.clicked.connect(self.categorize)
        self.layout().addWidget(self.cat_btn)

        self.cat_rename_btn = qtw.QPushButton("Categorize and Rename", self)
        self.cat_rename_btn.clicked.connect(self.categorize_and_rename)
        self.layout().addWidget(self.cat_rename_btn)

        self.show()

    def rename(self):
        self.name_label.setText("File renamed!")
        self.name_entry.setText("")
        time.sleep(2)
        self.close()

    def ignore(self):
        self.close()

    def categorize(self):
        move_file(self.file_path)
        self.close()

    def categorize_and_rename(self):
        self.close()


class MoverHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if isinstance(event, watchdog.events.FileModifiedEvent):
            logging.info(f"Found a file modified event: {event.src_path = }")

            window = FileManagerWindow(event.src_path)

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
    app = qtw.QApplication([])
    app.exec_()
    logging.info("File manager is active!")
    manager = DownloadFileManager(src_dir_path)
    manager.run()
