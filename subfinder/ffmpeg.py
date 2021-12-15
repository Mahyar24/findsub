#! /usr/bin/python3.9

"""
Mahyar@Mahyar24.com, Thu 19 Aug 2021.
"""


import bisect
import shutil
import subprocess
from pathlib import Path
from typing import Literal, Union

RATES = (8_000, 16_000, 32_000, 48_000)


class FFmpegError(BaseException):
    """We Should terminate the program if this error is raised."""


def find_sample_rate(rate: int) -> int:
    """
    Find best sample rate. Closest lower one.
    """
    index = bisect.bisect(RATES, rate)
    if index == 0:
        return RATES[0]
    return RATES[index - 1]


def suggest_sample_rate(movie: Path) -> Union[int, Literal[False]]:
    """
    If sample_rate was in (8000, 16000, 32000, 48000)Hz,
    we return a False and doesn't resample the rate; otherwise
    we will choose closest lower sample rate.
    """
    assert shutil.which("ffprobe") is not None, "Cannot find FFprobe."

    command = (
        f"ffprobe -hide_banner -select_streams a:0 -show_entries"
        f" stream=sample_rate -of default=noprint_wrappers=1:nokey=1 '{movie}'"
    )

    try:
        sample_rate = subprocess.check_output(
            command, shell=True, stderr=subprocess.DEVNULL, text=True
        ).strip()
    except subprocess.CalledProcessError:
        print("FFprobe cannot extract audio sample rate! It will set to 16,000.")
        return 16_000
    else:
        rate = int(float(sample_rate))
        if rate in RATES:
            return False
        return find_sample_rate(rate)


def extract_audio(movie: Path, cached_audio: Path) -> None:
    """
    Extracting audio of the movie with help of `FFmpeg`.
    16-bit. Mono. 32,000 Hz. Wav.
    """
    assert shutil.which("ffmpeg") is not None, "Cannot find FFmpeg."
    if rate := suggest_sample_rate(movie):
        command = f"ffmpeg -y -i '{movie}' -map a:0 -ar {rate} -acodec pcm_s16le -ac 1 '.audio.wav'"
    else:
        command = (
            f"ffmpeg -y -i '{movie}' -map a:0 -acodec pcm_s16le -ac 1 '.audio.wav'"
        )
    return_code = subprocess.call(
        command, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
    )
    if return_code:  # Error
        msg = "FFmpeg cannot extract audio! "
        if ":" in str(movie):
            msg += 'maybe because there is a ":" in filename!'

        raise FFmpegError(msg)

    Path(".audio.wav").rename(cached_audio)
