# cython: language_level=3
# cython: boundscheck=False
# cython: wraparound=False
# cython: cdivision=True

from libc.stdlib cimport malloc, free

import contextlib
import wave

import webrtcvad
from ffmpeg import RATES


def assert_wave(file):
    """
    asserting qualities, returning sample rate.
    """
    with contextlib.closing(wave.open(file, "rb")) as wav_file:
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
        return sample_rate, wav_file.getnframes()


cpdef list make_base(str file, unsigned int millisecond=20, float threshold=0.85):
    """
    We will use only this function externally.
    Make a timeline structure of when there is speech. For increasing the speed,
    this function based on threshold will decide that in every one second is
    there a human speech or not.
    """
    vad = webrtcvad.Vad()
    vad.set_mode(0)

    sample_rate, total_frames = assert_wave(file)

    cdef:
        bytes chunk
        unsigned int unit = 1_000 // millisecond
        unsigned long counter = 0
        unsigned long new_counter = 0
        unsigned long i = 0
        unsigned int j = 0
        unsigned int sec = 0
        double result
        unsigned int unit_sum = 0
        unsigned int num_frames = sample_rate * millisecond // 1000
        int *base_ms = <int *> malloc(sizeof(int) * (total_frames // num_frames))
    
    with contextlib.closing(wave.open(file, "rb")) as wav_file:
        chunk = wav_file.readframes(num_frames)
        while chunk:
            if len(chunk) == (num_frames * 2):
                base_ms[counter] = <int> vad.is_speech(chunk, sample_rate)
                counter += 1
            chunk = wav_file.readframes(num_frames)

    cdef int base[100_000][2]

    for sec, i in enumerate(range(0, counter, unit)):
        for j in range(unit):
            unit_sum += base_ms[i + j]
        result = <double> unit_sum / <double> unit
        if result >= threshold:
            base[new_counter] = [sec, sec + 1]
            new_counter += 1
        unit_sum = 0
    
    free(base_ms)    
    
    return (<list> base)[:new_counter]
