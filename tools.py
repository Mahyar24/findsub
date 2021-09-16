#! /usr/bin/python3.9

"""
Some tiny functions to use in `cli.py`.
Compatible with python3.9+.
Mahyar@Mahyar24.com, Thu 19 Aug 2021.
"""

import os
import shutil
from typing import Optional


def check_for_audio():
    """
    See if completed audio is present.
    """
    return ".audio_completed.wav" in os.listdir()


def clear(directory: Optional[str], audio: str) -> None:
    """
    Remove the directory and audio file.
    """
    if directory is not None:  #
        shutil.rmtree(
            directory
        )  # The directory should be empty but some cautious is not bad!
    os.remove(audio)


def rename_subs(results: dict[str, float], directory: str, move: bool) -> None:
    """
    Make the Subs directory and rename subtitles based on coverage.
    """
    try:
        os.mkdir("Subs")
    except FileExistsError:
        pass
    for i, sub in enumerate(results.keys()):
        new_name = f"Subs/{i + 1}.srt"
        if move:
            os.rename(os.path.join(directory, sub), new_name)
        else:
            try:
                shutil.copy(os.path.join(directory, sub), new_name)
            except shutil.SameFileError:
                new_name = new_name.removesuffix(".srt") + "_SUBFINDER.srt"
                shutil.copy(os.path.join(directory, sub), new_name)
        if (per := results[sub] * 100) >= 0.0:
            print(f"{new_name}: {per:.2f}%")
