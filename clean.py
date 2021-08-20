#! /usr/bin/python3.9

"""
This module's goal is to unzip, removes duplicate and convert subtitles to
UTF-8 and remove unnecessary junks.
Compatible with python3.9+. No third-party library is required, but having a dependency for
`Convert.sh` and `iconv` command underneath.
Mahyar@Mahyar24.com, Thu 19 Aug 2021.
"""

import hashlib
import os
import subprocess
import zipfile
from concurrent.futures import ALL_COMPLETED, ProcessPoolExecutor, wait
from typing import Optional


def hash_subtitles(directory: str) -> None:
    """
    Hash the subtitles content by using md5 and then renaming it to the hexdigest of hash.
    """
    for file in os.listdir(directory):
        if file.endswith(".srt"):
            file_name = os.path.join(directory, file)
            with open(file_name, "rb") as subtitle:
                data = subtitle.read()
            hash_name = hashlib.md5(data).hexdigest() + ".srt"
            os.rename(file_name, os.path.join(directory, hash_name))


def delete_bad_files(directory: str) -> None:
    """
    Delete any non-srt files.
    """
    for file in os.listdir(directory):
        if not file.endswith(".srt"):
            os.remove(os.path.join(directory, file))


def unzip_remove(zip_file: str) -> Optional[str]:
    """
    Unzip, extract all and removing zip file. If extraction fails, remove
    the zip file and return None, else, delete non-srt files and change
    the name of subtitles to their md5 hash hexdigest.
    """
    directory = os.path.abspath(os.path.basename(zip_file).split(".")[0])
    try:
        with zipfile.ZipFile(zip_file, "r") as file:
            file.extractall(
                directory
            )  # Must extract every zip file to one directory otherwise maybe some
            # subtitle with duplicate name and different content gets remove.
    except zipfile.BadZipfile:
        os.remove(zip_file)
        return None
    os.remove(zip_file)
    delete_bad_files(directory)
    hash_subtitles(directory)
    return directory


def unzip_all_and_hash(zip_files: list[str]) -> list[str]:
    """
    Unzip and calculate hash for renaming concurrently.
    Returning list of successfully processed subtitles.
    """
    with ProcessPoolExecutor() as executor:
        tasks = [
            executor.submit(unzip_remove, zip_file)
            for zip_file in zip_files
            if zip_file.endswith(".zip")
        ]
        wait(tasks, return_when=ALL_COMPLETED)
    return [result for task in tasks if (result := task.result()) is not None]


def iconv_subtitles(directory) -> None:
    """
    Converting non UTF-8 srt files to UTF-8. Based on `Convert.sh`.
    Because we are in subtitle directory, we must run shell script
    with leading two dots. (../Sample.sh)
    """
    subprocess.call(
        f"/home/mahyar/Works/ShittyStuff/SubFinder/Convert.sh {directory!r}",
        shell=True,
        stdout=subprocess.DEVNULL,
    )


def move_up(directories: list[str], main_directory: str) -> None:
    """
    Moving up subtitles and delete the empty directory.
    """
    for directory in directories:
        for file in os.listdir(directory):
            os.rename(
                os.path.join(directory, file), os.path.join(main_directory, file)
            )  # It will removes additional duplicates too.
        os.rmdir(directory)


def prepare_files(directory: str) -> None:
    """
    We will use only this function externally.
    Check other functions docstring.
    """
    files = [os.path.abspath(os.path.join(directory, f)) for f in os.listdir(directory)]
    dirs = unzip_all_and_hash(files)
    move_up(dirs, directory)
    iconv_subtitles(directory)
