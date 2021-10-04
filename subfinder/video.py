#! /usr/bin/python3.9

"""
This module's goal is to make a data structure of when there is a human speech in the movie.
Compatible with python3.9+.
`webrtcvad` library is required. -> https://pypi.org/project/webrtcvad/
`FFmpeg` is required. -> https://www.ffmpeg.org/
`FFprobe` is required. -> https://ffmpeg.org/ffprobe.html
Some of the functions here are copied from https://github.com/wiseman/py-webrtcvad. (MIT License)
Mahyar@Mahyar24.com, Thu 19 Aug 2021.
"""

import bisect
import contextlib
import os
import shutil
import signal
import subprocess
import wave
from datetime import timedelta
from typing import Iterator, Literal, Union

import webrtcvad  # type: ignore

RATES = (8_000, 16_000, 32_000, 48_000)


def find_sample_rate(rate: int) -> int:
    """
    Find best sample rate. Closest lower one.
    """
    index = bisect.bisect(RATES, rate)
    if index == 0:
        return RATES[0]
    return RATES[index - 1]


def suggest_sample_rate(movie: str) -> Union[int, Literal[False]]:
    """
    If sample_rate was in (8000, 16000, 32000, 48000)Hz,
    we return a False and doesnt resample the rate; otherwise
    we will choose closest lower sample rate.
    """
    assert shutil.which("ffprobe") is not None, "Cannot find FFprobe."
    command = (
        f"ffprobe -hide_banner -select_streams a:0 -show_entries"
        f" stream=sample_rate -of default=noprint_wrappers=1:nokey=1 {movie!r}"
    )
    try:
        sample_rate = subprocess.check_output(
            command, shell=True, stderr=subprocess.DEVNULL, text=True
        ).strip()
    except subprocess.CalledProcessError:
        print("FFprobe cannot extract audio sample rate! ")
        return 16_000
    else:
        rate = int(float(sample_rate))
        if rate in RATES:
            return False
        return find_sample_rate(rate)


def extract_audio(movie: str, gpu_acceleration: bool = False) -> None:
    """
    Extracting audio of the movie with help of `FFmpeg`.
    16-bit. Mono. 32,000 Hz. Wav.
    """
    assert shutil.which("ffmpeg") is not None, "Cannot find FFmpeg."
    cuda = "-hwaccel cuda" if gpu_acceleration else ""
    if rate := suggest_sample_rate(movie):
        command = f"ffmpeg -y -i {movie!r} {cuda} -ar {rate} -acodec pcm_s16le -ac 1 '.audio.wav'"
    else:
        command = f"ffmpeg -y -i {movie!r} {cuda} -acodec pcm_s16le -ac 1 '.audio.wav'"
    return_code = subprocess.call(
        command, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
    )
    if return_code:  # Error
        msg = "FFmpeg cannot extract audio! "
        if ":" in movie:
            msg += 'maybe because there is a ":" in filename!'
        elif gpu_acceleration:
            msg += "maybe because FFmpeg is not compiled with cuda support!"
        print(msg)
        os.kill(
            os.getppid(), signal.SIGTERM
        )  # Hack. Killing program within child process.
    os.rename(".audio.wav", ".audio_completed.wav")


def generate_chunk(
    frame_duration_ms: int, audio: bytes, sample_rate: int
) -> Iterator[bytes]:
    """
    Slicing was to chunks of data based on frame duration.
    """
    num = int(sample_rate * (frame_duration_ms / 1000.0) * 2)
    offset = 0
    while offset + num < len(audio):  # TODO: use Cython.
        yield audio[offset : offset + num]
        offset += num


def read_wave(file: str) -> tuple[bytes, int]:
    """
    Reading wav file, asserting qualities, returning data.
    """
    with contextlib.closing(wave.open(file, "rb")) as wav_file:
        sample_rate = wav_file.getframerate()
        pcm_data = wav_file.readframes(
            wav_file.getnframes()
        )  # TODO: don't loading all data in memory.
        return pcm_data, sample_rate


def make_base(
    file: str, millisecond: int = 20, threshold: float = 0.85
) -> list[tuple[int, int]]:
    """
    We will use only this function externally.
    Make a timeline structure of when there is speech. For increasing the speed,
    this function based on threshold will decide that in every one second is
    there a human speech or not.
    """
    data, rate = read_wave(file)
    vad = webrtcvad.Vad()
    vad.set_mode(0)

    unit = 1_000 // millisecond
    base_ms = [
        vad.is_speech(chunk, rate) for chunk in generate_chunk(millisecond, data, rate)
    ]
    base_s = [base_ms[i : i + unit] for i in range(0, len(base_ms), unit)]
    base = []
    for i, second in enumerate(base_s):
        if sum(second) / len(second) > threshold:
            base.append(
                (
                    i,
                    i + 1,
                )
            )
    return base
