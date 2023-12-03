# requirements:
# - progressbar2

import os
import subprocess
import tempfile
import time
import urllib.request
from pathlib import Path

try:
    HAS_GDOWN = False
    import gdown
    HAS_GDOWN = True
except ImportError:
    print("No gdown")

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
    FILE_NAME: str = None
    TARGET_DIR: str

    @classmethod
    def download(cls):
        if Path(cls.file_name).exists():
            print(f"{cls.file_name} already exists, skipping download...")
            return
        print(f"Downloading {cls.url} to {cls.file_name}...")
        if cls.url.startswith("https://drive.google.com"):
            gdown.download(cls.url, cls.file_name, quiet=False)
        else:
            urllib.request.urlretrieve(cls.url, cls.file_name, ProgressBar())
        print("Done.")

    @classmethod
    @property
    def url(cls):
        if not cls.URL:
            raise ValueError("URL is not set")
        return cls.URL

    @classmethod
    @property
    def file_name(cls):
        return cls.FILE_NAME or cls.URL.rsplit("/", 1)[-1]


class Executable(Object):
    @classmethod
    def run(cls):
        print(f"Running {cls.file_name}...")
        # subprocess.run(cls.file_name)
        code = os.system(cls.file_name)

        if code == 0:
            print("Exited successfully.")

        print(f"Error {code} while running {cls.file_name}")
        if input("Abort? [Yn]").lower() not in ("n", "no"):
            print("Exiting early...")
            exit(1)
        print("Moving on...")



class Setup(Object):
    TARGET_DIR: str
    CREATE_START_MENU_SHORTCUT: bool = True
    CREATE_DESKTOP_SHORTCUT: bool = True

class Archive(Object):
    @classmethod
    def extract(cls):
        try:
            import winreg

            # Check if 7zip is installed and where
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, "SOFTWARE\\7-Zip") as key:
                value, _ = winreg.QueryValueEx(key, "Path")
                print(value)
                p7zip = Path(value) / "7z.exe"
        except ModuleNotFoundError:
            print("No winreg")

class SongsPacksCollection(Archive):
    pass


class ITGMania(Executable):
    URL = "https://github.com/itgmania/itgmania/releases/download/v0.7.0/ITGmania-0.7.0-Windows-no-songs.exe"

class DDRPadDDRSongsPack(SongsPacksCollection):
    URL = "https://drive.google.com/file/d/1uPgFx83xV5MzZ8rEy-Z1_SH1tJEICjv6/view"

cwd = os.getcwd()

# TMP
fake_tmp = Path(R"C:\Users\savat\tmp\sm-wizard")
fake_tmp.mkdir(parents=True, exist_ok=True)

TARGET_GAME_DIRECTORY = R"C:\Games\PC\ITGMania-test"
TARGET_SONGS_DIRECTORY = R"C:\Games\PC\ITGMania-test\Songs"
TARGET_SKINS_DIRECTORY = R"C:\Games\PC\ITGMania-test\Themes"

with tempfile.TemporaryDirectory() as tmpdirname:
    os.chdir(tmpdirname)

    # TMP
    os.chdir(fake_tmp)

    # ITGMania.download()
    # ITGMania.run()

    DDRPadDDRSongsPack.extract()

    os.chdir(cwd)
