#! /usr/bin/python3.9

"""
This module's goal is to make a data structure of when there is a human speech in the movie.
`webrtcvad` library is required. -> https://pypi.org/project/webrtcvad/
`FFmpeg` is required. -> https://www.ffmpeg.org/
`FFprobe` is required. -> https://ffmpeg.org/ffprobe.html
Some functions here are copied from https://github.com/wiseman/py-webrtcvad. (MIT License)
Compatible with python3.9+.
Mahyar@Mahyar24.com, Thu 19 Aug 2021.
"""

import contextlib
import wave
from pathlib import Path
from typing import Iterable

import webrtcvad  # type: ignore

from .ffmpeg import RATES


def generate_chunk(
    file: Path, frame_duration_ms: int, sample_rate: int
) -> Iterable[bool]:
    """
    Slicing was to chunk of data based on frame duration.
    """
    vad = webrtcvad.Vad()
    vad.set_mode(0)

    num_frames = int(sample_rate * (frame_duration_ms / 1000.0))
    with contextlib.closing(wave.open(str(file), "rb")) as wav_file:
        with contextlib.suppress(Exception):
            while chunk := wav_file.readframes(num_frames):
                yield vad.is_speech(chunk, sample_rate)


def assert_wave(file: Path) -> int:
    """
    asserting qualities, returning sample rate.
    """
    with contextlib.closing(wave.open(str(file), "rb")) as wav_file:
        num_channels = wav_file.getnchannels()

        assert (
            num_channels == 1
        ), f"Number of Channels must be one, not {num_channels!r}."

        sample_width = wav_file.getsampwidth()
        assert sample_width == 2, f"Width must be two, not {sample_width!r}."

        sample_rate = wav_file.getframerate()
        assert (
            sample_rate in RATES
        ), f"Sample Rate must be in {RATES}, not {sample_rate!r}."

        return sample_rate


def make_base(
    file: Path, millisecond: int = 20, threshold: float = 0.85
) -> list[tuple[int, int]]:
    """
    We will use only this function externally.
    Make a timeline structure of when there is speech. For increasing the speed,
    this function based on threshold will decide that in every one second is
    there a human speech or not.
    """
    rate = assert_wave(file)

    unit = 1_000 // millisecond

    base_ms = list(generate_chunk(file, millisecond, rate))
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
