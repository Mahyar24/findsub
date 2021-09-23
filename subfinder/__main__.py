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

import multiprocessing
import os
from typing import Optional

from clean import iconv_subtitles, prepare_files
from cli import find_language, parsing_args
from core import match_all
from download import get_files
from subtitles import extract_subtitle_times
from tools import check_for_audio, clear, rename_subs
from video import extract_audio, make_base


def main(  # TODO: break main function into more compact functions.
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
        clear_audio = True
        audio = ".audio_completed.wav"
        if not check_for_audio():
            wait_for_audio = True
            process = multiprocessing.Process(
                target=extract_audio, args=(file,), daemon=True
            )
            process.start()
            print("Audio extraction begins.")
    else:
        clear_audio = False  # We shouldn't remove user's audio.

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
            _, directory = get_files(lang=language, link=subscene)
        prepare_files(directory)
    else:
        directory = subtitles_directory
        iconv_subtitles(directory)

    try:
        sub_time_structures = extract_subtitle_times(directory)
    except UnicodeError:
        clear(
            directory if subtitles_directory is None else None,
            audio if clear_audio else "",
        )  # First parameter assure that we don't accidentally delete
        # already existed subtitle directory.
        raise

    if wait_for_audio:
        print("Waiting for audio extraction to finish.")
        # noinspection PyUnboundLocalVariable
        process.join()
        print("Audio Extraction finished.")
    movie_time_structure = make_base(audio)
    results = match_all(movie_time_structure, sub_time_structures)
    rename_subs(
        results, directory, move=subtitles_directory is None
    )  # If subtitle_directory is present then we just copy files
    # and remain the original subtitle folder intact.
    clear(
        directory if subtitles_directory is None else None, audio if clear_audio else ""
    )
    print("Done.")


if __name__ == "__main__":
    args = parsing_args()
    assert os.path.isfile(args.file), f"Cannot find {args.file!r}"
    try:
        os.chdir(os.path.dirname(args.file))  # CHANGE THE DIRECTORY.
    except FileNotFoundError:
        pass  # Already at place.

    if args.subtitles_directory is None:
        lang = find_language(args.language)
    else:
        lang = ""

    main(
        file=os.path.basename(args.file),
        language=lang,
        audio=args.audio,
        subscene=args.subscene,
        subtitles_directory=args.subtitles_directory,
    )
