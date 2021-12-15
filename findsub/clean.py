#! /usr/bin/python3.9

"""
This module's goal is to unzip, removes duplicate and convert subtitles to
UTF-8 and remove unnecessary junks.
Compatible with python3.9+. No third-party library is required, but having a dependency for
`Convert.sh` and `iconv` command underneath.
`iconv` is required. -> https://www.gnu.org/software/libiconv/
also Bash is in need!
Compatible with python3.9+.
Mahyar@Mahyar24.com, Thu 19 Aug 2021.
"""

import hashlib
import shutil
import subprocess
import zipfile
from concurrent.futures import ALL_COMPLETED, ProcessPoolExecutor, wait
from pathlib import Path
from typing import Optional


def hash_subtitles(directory: Path) -> None:
    """
    Hash the subtitles content by using md5 and then renaming it to the hexdigest of hash.
    """
    for item in directory.iterdir():
        if item.is_file() and item.name.endswith(".srt"):
            with open(item, "rb") as subtitle:
                data = subtitle.read()
            hash_name = hashlib.md5(data).hexdigest() + ".srt"
            item.rename(directory / hash_name)


def delete_bad_files(directory: Path) -> None:
    """
    Delete any non-srt files.
    """
    for item in directory.iterdir():
        if item.is_file() and not item.name.endswith(".srt"):
            item.unlink(missing_ok=True)


def unzip_remove(zip_file: Path) -> Optional[Path]:
    """
    Unzip, extract all and removing zip file. If extraction fails, remove
    the zip file and return None, else, delete non-srt files and change
    the name of subtitles to their md5 hash hexdigest.
    """
    directory = zip_file.parent / zip_file.stem
    try:
        with zipfile.ZipFile(zip_file, "r") as file:
            # Must extract every zip file to one directory otherwise maybe some
            # subtitle with duplicate name and different content gets remove.
            file.extractall(directory)
    except zipfile.BadZipfile:
        zip_file.unlink()
        return None
    else:

        zip_file.unlink()
        delete_bad_files(directory)
        hash_subtitles(directory)

        return directory


def unzip_all_and_hash(zip_files: list[Path]) -> list[Path]:
    """
    Unzip and calculate hash for renaming concurrently.
    Returning list of successfully processed subtitles.
    """
    with ProcessPoolExecutor() as executor:
        tasks = [
            executor.submit(unzip_remove, zip_file)
            for zip_file in zip_files
            if zip_file.name.endswith(".zip")
        ]
        wait(tasks, return_when=ALL_COMPLETED)
    return [result for task in tasks if (result := task.result()) is not None]


def iconv_subtitles(directory: Path) -> None:
    """
    Converting non UTF-8 srt files to UTF-8. Based on `Convert.sh`.
    Because we are in subtitle directory, we must run shell script
    with leading two dots. (../Sample.sh)
    """
    script_path = Path(__file__).parent / "scripts/Convert.sh"
    subprocess.call(
        f'{script_path} "{directory}"',
        shell=True,
        stdout=subprocess.DEVNULL,
    )


def move_up(directories: list[Path]) -> None:
    """
    Moving up subtitles and delete the empty directory.
    """
    for directory in directories:
        for item in directory.iterdir():
            if item.is_file():
                item.rename(item.absolute().parents[1] / item.name)
            else:
                shutil.rmtree(item)
        directory.rmdir()


def prepare_files(directory: Path) -> None:
    """
    We will use only this function externally.
    Check other functions docstring.
    """
    files = list(directory.iterdir())
    dirs = unzip_all_and_hash(files)
    move_up(dirs)
    iconv_subtitles(directory)
