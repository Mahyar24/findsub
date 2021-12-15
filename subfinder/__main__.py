#! /usr/bin/python3.9

"""
This package's goal is to download all subtitles with a specific language
of a movie from Subscene.com and then check every one of them to ranks them
by synchronous.
How? It will download subtitles and simultaneously extract audio of the file
by using `FFMPEG`, after that we check when there is a possible human speech
and make a timeline of it. Finally, we check how much of a time when there is
a possible speech each of the subtitles has a text.

Required PyPI Packages:
    `aiofiles` library is required. -> https://pypi.org/project/aiofiles/
    `aiohttp` library is required. -> https://pypi.org/project/aiohttp/
    `beautifulsoup4` library is required. -> https://pypi.org/project/beautifulsoup4/
    `webrtcvad` library is required. -> https://pypi.org/project/webrtcvad/
    `IMDbPY` library is required. -> https://pypi.org/project/IMDbPY/
    `srt` library is required. -> https://pypi.org/project/srt/
    `Cython` is required. -> https://pypi.org/project/Cython/
    `tqdm` library is required. -> https://pypi.org/project/tqdm/
Required External Tools:
    `FFmpeg` is required. -> https://www.ffmpeg.org/
    `FFprobe` is required. -> https://ffmpeg.org/ffprobe.html
    And also Bash!

Some functions here are copied from https://github.com/wiseman/py-webrtcvad.

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
from pathlib import Path
from typing import Optional

from .clean import iconv_subtitles, prepare_files
from .cli import parsing_args
from .download import Downloader
from .ffmpeg import extract_audio
from .movie import Movie
from .pycore import match_all
from .pyvideo import make_base
from .subtitles import extract_subtitle_times
from .tools import clear, make_subs_dir


def main(
    file: Path,
    language: str,
    audio: Optional[Path] = None,
    subscene: Optional[str] = None,
    subtitles_directory: Optional[Path] = None,
) -> None:
    """
    Main entry point. It should not be used within python code. Designed for CLI.
    """

    movie = Movie(file)

    cached_audio = movie.dir / f".{movie.filename_hash}_audio_completed.wav"

    if audio is None:  # Check for extracted audio file.
        if cached_audio.is_file():
            audio = cached_audio

    if audio is None:
        process = multiprocessing.Process(
            target=extract_audio, args=(movie, cached_audio), daemon=True
        )
        process.start()
        print("Audio extraction begins.")

    # If user already has a directory of subtitles, we must not move them to the Subs.
    move = True
    if subtitles_directory is None:
        subtitles_directory = Downloader(
            movie=movie, lang=language, link=subscene
        ).download()
        prepare_files(subtitles_directory)
    else:
        move = False
        iconv_subtitles(subtitles_directory)

    try:
        print("Examining subtitles.", end=" ", flush=True)
        sub_time_structures = extract_subtitle_times(subtitles_directory)
    except UnicodeError:
        clear(subtitles_directory, cached_audio, remove=move)
        raise
    else:
        print("Done.")

    if audio is None:
        print("Waiting for audio extraction to finish.", end=" ", flush=True)
        # noinspection PyUnboundLocalVariable
        process.join()
        audio = cached_audio
        print("Done.")

    print("Voice Activity Detector started the analysis.", end=" ", flush=True)
    movie_time_structure = make_base(audio)
    print("Done.")

    results = match_all(movie_time_structure, sub_time_structures)

    make_subs_dir(subtitles_directory, results, move=move)
    clear(subtitles_directory, cached_audio, remove=move)

    print("Done.")


def run():
    """
    EntryPoint of Application.
    """
    args = parsing_args()

    assert args.file.is_file(), f"Cannot find {args.file!r}"
    if args.audio is not None:
        assert args.file.is_file(), f"Cannot find {args.file!r}"
    if args.subtitles_directory is not None:
        assert (
            args.subtitles_directory.is_dir()
        ), f"Cannot find {args.subtitles_directory!r}"

    main(
        file=args.file,
        language=args.language,
        audio=args.audio,
        subscene=args.subscene,
        subtitles_directory=args.subtitles_directory,
    )


if __name__ == "__main__":
    run()
