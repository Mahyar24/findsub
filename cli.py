#! /usr/bin/python3.9

"""
This package's goal is to .... TODO: complete this.
Compatible with python3.9+.
Mahyar@Mahyar24.com, Thu 19 Aug 2021.
"""


import argparse
import multiprocessing
import os
from typing import Optional

from clean import prepare_files
from core import match_all
from download import get_files
from subtitles import extract_subtitle_times
from tools import check_for_audio, clear, rename_subs
from video import extract_audio, make_base


def parsing_args() -> argparse.Namespace:
    """
    Parsing the passed arguments, read help (-h, --help) for further information.
    """
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "file",
        help="Select desired movie.",
    )

    parser.add_argument(
        "-l",
        "--language",
        default="farsi_persian",
        help="Desired language for subtitle.",
    )

    parser.add_argument("-s", "--subscene", help="URL of subscene for the movie.")

    parser.add_argument(
        "-a",
        "--audio",
        help="If extracted audio is available, use the path to speed up program.",
    )

    return parser.parse_args()


def main(
    file: str,
    language: str,
    audio: Optional[str] = None,
    subscene: Optional[str] = None,
) -> None:
    """
    Main entry point. It should not used within python code. Designed for CLI.
    """
    wait_for_audio = False
    if audio is None:
        audio = ".audio_completed.wav"
        if not check_for_audio():
            process = multiprocessing.Process(
                target=extract_audio, args=(file,), daemon=True
            )
            process.start()
            wait_for_audio = True
    if subscene is None:
        try:
            _, directory = get_files(lang=language, file_name=file)
        except ValueError as error:
            raise RuntimeError(
                "Cannot get subtitles, please use --subscene option."
            ) from error
    else:
        _, directory = get_files(
            lang="farsi_persian", link=subscene
        )  # TODO: language json.
    prepare_files(directory)
    sub_time_structures = extract_subtitle_times(directory)
    if wait_for_audio:
        process.join()
    movie_time_structure = make_base(audio)
    results = match_all(movie_time_structure, sub_time_structures)
    rename_subs(results, directory)
    clear(directory)


if __name__ == "__main__":
    args = parsing_args()
    assert os.path.isfile(args.file), f"Cannot find {args.file!r}"
    os.chdir(os.path.dirname(args.file))  # CHANGE THE DIRECTORY.
    main(
        file=os.path.basename(args.file),
        language=args.language,
        audio=args.audio,
        subscene=args.subscene,
    )
