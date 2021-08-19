#! /usr/bin/python3.9

"""
Some tiny functions to use in `cli.py`.
Compatible with python3.9+.
Mahyar@Mahyar24.com, Thu 19 Aug 2021.
"""

import os
import shutil


def check_for_audio():
    """
    See if completed audio is present.
    """
    return ".audio_completed.wav" in os.listdir()


def clear(directory: str) -> None:
    """
    Remove the directory and audio file.
    """
    shutil.rmtree(
        directory
    )  # The directory should be empty but some cautious is not bad!
    os.remove(".audio_completed.wav")


def rename_subs(results: dict[str, float], directory: str) -> None:
    """
    Make the Subs directory and rename subtitles based on coverage.
    """
    os.mkdir("Subs")
    for i, sub in enumerate(results.keys()):
        os.rename(os.path.join(directory, sub), f"Subs/{i + 1}.srt")
