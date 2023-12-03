# requirements:
# - progressbar2

import urllib.request
import tempfile
from pathlib import Path
import time
import subprocess
import os

try:
    from progressbar import DataTransferBar

    class ProgressBar(DataTransferBar):
        def __call__(self, block_num, block_size, total_size):
            self.max_value = total_size + 1
            downloaded = block_num * block_size
            if downloaded < total_size:
                self.update(downloaded)
            else:
                self.finish()

except ImportError:

    class ProgressBar:
        DELTA_NEEDED = 1

        def __init__(self):
            self.last_update = time.time()

        def __call__(self, block_num, block_size, total_size):
            now = time.time()
            if now - self.last_update < self.DELTA_NEEDED:
                return
            self.last_update = now
            downloaded = block_num * block_size
            downloaded = sizeof_fmt(downloaded)
            total_size = sizeof_fmt(total_size)
            print(f"Downloaded {downloaded} of {total_size}...")


def sizeof_fmt(num, suffix="B"):
    for unit in ("", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"):
        if abs(num) < 1024.0:
            return f"{num:3.1f}{unit}{suffix}"
        num /= 1024.0
    return f"{num:.1f}Yi{suffix}"


class Object:
    URL: str
    FILE_NAME: str
    TARGET_DIR: str

    @classmethod
    def download(cls):
        print(f"Downloading {cls.url} to {cls.file_name}...")
        urllib.request.urlretrieve(cls.url, cls.file_name, ProgressBar())
        print("Done.")

    @property
    def url(self):
        if not self.URL:
            raise ValueError("URL is not set")
        return self.URL

    @property
    def file_name(self):
        return self.FILE_NAME or self.URL.rsplit("/", 1)[-1]


class Executable(Object):
    @classmethod
    def run(cls):
        print(f"Running {cls.FILE_NAME}...")
        subprocess.run(cls.FILE_NAME)
        print("Done.")


class Setup(Object):
    TARGET_DIR: str
    CREATE_START_MENU_SHORTCUT: bool = True
    CREATE_DESKTOP_SHORTCUT: bool = True


class ITGMania(Executable):
    URL = "https://github.com/itgmania/itgmania/releases/download/v0.7.0/ITGmania-0.7.0-Windows-no-songs.exe"


cwd = os.getcwd()
with tempfile.TemporaryDirectory() as tmpdirname:
    os.chdir(tmpdirname)

    ITGMania.download()
    ITGMania.run()

    os.chdir(cwd)
