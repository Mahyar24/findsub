#! /usr/bin/python3.9

"""
This module's goal is to make a data structure of when there is a human speech in the movie.
Compatible with python3.9+.
`webrtcvad` library is required. -> https://pypi.org/project/webrtcvad/
`ffmpeg` is required. -> https://www.ffmpeg.org/
Some of the functions here are copied from https://github.com/wiseman/py-webrtcvad. (MIT License)
Mahyar@Mahyar24.com, Thu 19 Aug 2021.
"""

import contextlib
import os
import shutil
import signal
import subprocess
import wave
from datetime import timedelta
from typing import Iterator

import webrtcvad  # type: ignore


def extract_audio(movie: str) -> None:
    """
    Extracting audio of the movie with help of `ffmpeg`.
    16-bit. Mono. 32,000 Hz. Wav.
    """
    assert shutil.which("ffmpeg") is not None, "Cannot find ffmpeg."
    command = f"ffmpeg -y -i {movie!r} -ar 32000 -acodec pcm_s16le -ac 1 '.audio.wav'"
    return_code = subprocess.call(
        command, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
    )
    if return_code:  # Error
        msg = "FFMPEG cannot extract audio! "
        if ":" in movie:
            msg += 'maybe because there is a ":" in filename!'
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
    timestamp = 0.0
    duration = (float(num) / sample_rate) / 2.0
    while offset + num < len(audio):
        yield audio[offset : offset + num]
        timestamp += duration
        offset += num


def read_wave(file: str) -> tuple[bytes, int]:
    """
    Reading wav file, asserting qualities, returning data.
    """
    with contextlib.closing(wave.open(file, "rb")) as wav_file:
        num_channels = wav_file.getnchannels()
        assert num_channels == 1
        sample_width = wav_file.getsampwidth()
        assert sample_width == 2
        sample_rate = wav_file.getframerate()
        assert sample_rate in (8000, 16000, 32000, 48000)
        pcm_data = wav_file.readframes(wav_file.getnframes())
        return pcm_data, sample_rate


def make_base(
    file: str, millisecond: int = 20, threshold: float = 0.85
) -> list[tuple[timedelta, timedelta]]:
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
            base.append((timedelta(seconds=i), timedelta(seconds=i + 1)))
    return base
