#! /usr/bin/python3.9

"""
This package's goal is to download all subtitles with a specific language
of a movie from Subscene.com and then check every one of them to ranks them
by synchronous.
How? It will download subtitles and simultaneously extract audio of the file
by using `FFMPEG`, after that we check when there is a possible human speech
and make a timeline of it. Finally we check how much of a time when there is
a possible speech each of the subtitles has a text.

Required PyPI Packages:
    `aiofiles` library is required. -> https://pypi.org/project/aiofiles/
    `aiohttp` library is required. -> https://pypi.org/project/aiohttp/
    `beautifulsoup4` library is required. -> https://pypi.org/project/beautifulsoup4/
    `webrtcvad` library is required. -> https://pypi.org/project/webrtcvad/
    `IMDbPY` library is required. -> https://pypi.org/project/IMDbPY/
    `srt` library is required. -> https://pypi.org/project/srt/
Required External Tools:
    `ffmpeg` is required. -> https://www.ffmpeg.org/
    And also Bash!

Some of the functions here are copied from https://github.com/wiseman/py-webrtcvad.

Usage:
    subfinder <file>. -> makes a `Subs` folder and put ranked subtitles in it
    subfinder <file> -a/--audio extracted_audio.wav -> same as last one but
        using already extracted audio. (faster!)
    subfinder -l/--language en/english <file> -> getting english subtitles.
        default is "Farsi/Persian".
    subfinder -s/--subscene <subscene-link> <file> -> no link suggestion. (faster!)
    subfinder -d/--subtitles-directory <path-of-downloaded-subtitles> <file> ->
        using already download subtitles.
Compatible with python3.9+.
Mahyar@Mahyar24.com, Thu 19 Aug 2021.
"""


import argparse
import multiprocessing
import os
from typing import Optional

from clean import iconv_subtitles, prepare_files
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
    group_link_dir = (
        parser.add_mutually_exclusive_group()
    )  # Link or directory, not both!

    parser.add_argument(
        "file",
        help="Select desired movie.",
    )

    parser.add_argument(  # TODO: add real language support.
        "-l",
        "--language",
        default="farsi_persian",
        help="Desired language for subtitle.",
    )

    group_link_dir.add_argument(
        "-s", "--subscene", help="URL of subscene for the movie."
    )

    group_link_dir.add_argument(
        "-d",
        "--subtitles-directory",
        type=os.path.abspath,  # type: ignore # Make it absolute path.
        help="Check matching of subtitles in directory with movie.",
    )

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
    subtitles_directory: Optional[str] = None,
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
            print("Audio extraction begins.")
            wait_for_audio = True
    if subtitles_directory is None:
        if subscene is None:
            try:
                _, directory = get_files(lang=language, file_name=file)
            except ValueError as error:
                raise RuntimeError(
                    "Cannot get subtitles, please use --subscene option."
                ) from error
            except NotImplementedError:  # Subtitle with desired language didn't found.
                raise
        else:
            _, directory = get_files(
                lang="farsi_persian", link=subscene
            )  # TODO: language json.
        prepare_files(directory)
    else:
        directory = subtitles_directory
        iconv_subtitles(directory)
    sub_time_structures = extract_subtitle_times(directory)
    if wait_for_audio:
        process.join()
    print("Matching Algorithm started.")
    movie_time_structure = make_base(audio)
    results = match_all(movie_time_structure, sub_time_structures)
    rename_subs(results, directory)
    clear(directory, audio)
    print("Done.")


if __name__ == "__main__":
    args = parsing_args()
    assert os.path.isfile(args.file), f"Cannot find {args.file!r}"
    try:
        os.chdir(os.path.dirname(args.file))  # CHANGE THE DIRECTORY.
    except FileNotFoundError:
        pass  # Already at place.

    main(
        file=os.path.basename(args.file),
        language=args.language,
        audio=args.audio,
        subscene=args.subscene,
        subtitles_directory=args.subtitles_directory,
    )
