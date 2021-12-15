#! /usr/bin/python3.9

"""
Some tiny functions to use in `__main__.py`.
Compatible with python3.9+.
Mahyar@Mahyar24.com, Thu 19 Aug 2021.
"""

import json
import math
import os
import shutil
from pathlib import Path

from .movie import Movie


def emergency_cleanup(movie: Movie) -> None:
    """
    Clean all cached and unused file and directories in case of a sudden failure.
    """
    completed_audio = movie.dir / f".{movie.filename_hash}_audio_completed.wav"
    uncompleted_audio = movie.dir / f".{movie.filename_hash}_audio.wav"
    hidden_sub_dir = movie.dir / f".{movie.filename_hash}"

    completed_audio.unlink(missing_ok=True)
    uncompleted_audio.unlink(missing_ok=True)

    try:
        shutil.rmtree(hidden_sub_dir)
    except FileNotFoundError:
        pass


def clear(directory: Path, cached_audio: Path, remove: bool) -> None:
    """
    Remove the directory and audio file.
    """
    if remove:
        shutil.rmtree(
            directory
        )  # The directory should be empty but some cautious is not bad!

    cached_audio.unlink(missing_ok=True)


def find_zero_pad_number(length_of_subtitles: int) -> int:
    """
    Finding needed length of zeros. 123 files -> 1: 001; so it needs two leading zero.
    """
    return int(math.log10(length_of_subtitles)) + 1


def make_subs_dir(
    directory: Path, results: dict[str, float], move: bool = True
) -> None:
    """
    Make the Subs directory and rename subtitles based on coverage.
    """
    base_dir = directory.parent.absolute()
    subs = base_dir / "Subs"

    try:
        os.mkdir(subs)
    except FileExistsError:
        pass

    zero_pad_num = find_zero_pad_number(len(results))

    info: dict[str, dict[str, str]] = {
        "Subs": {},
        "FindSub": {
            "GitHub": "https://github.com/mahyar24/findsub",
            "PyPI": "https://pypi.org/project/findsub/",
            "E-Mail": "Mahyar@Mahyar24.com",
        },
    }

    for i, sub in enumerate(results.keys()):

        old_file = directory / sub
        new_name = f"{i + 1}".zfill(zero_pad_num) + ".srt"
        new_file = subs / new_name

        if move:
            old_file.rename(new_file)
        else:
            try:
                shutil.copy(old_file, new_file)
            except shutil.SameFileError:
                pass

        if results[sub] >= 0.0:  # If synchronous ratio became negative!
            print(f"{new_name}: {results[sub]:.2%}")
            info["Subs"][new_name] = f"{results[sub]:.2%}"

    with open(subs / "FindSub.json", "w", encoding="utf-8") as info_file:
        json.dump(info, info_file, indent=4)
