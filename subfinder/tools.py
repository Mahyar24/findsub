#! /usr/bin/python3.9

"""
Some tiny functions to use in `cli.py`.
Compatible with python3.9+.
Mahyar@Mahyar24.com, Thu 19 Aug 2021.
"""

import json
import math
import os
import shutil
from pathlib import Path


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
