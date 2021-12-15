#! /usr/bin/python3.9

"""
This module's goal is to calculate mutual percentage of time between two data structure
based on `subtitle.py` module. It will show how much they are potentially synchronous.
`tqdm` library is required. -> https://pypi.org/project/tqdm/
Compatible with python3.9+.
Mahyar@Mahyar24.com, Thu 19 Aug 2021.
"""

from concurrent.futures import ProcessPoolExecutor, as_completed
from datetime import timedelta

from tqdm import tqdm  # type: ignore

from .core import match


def match_all(
    movie_time: list[tuple[int, int]],
    sub_times: dict[str, list[tuple[timedelta, timedelta]]],
) -> dict[str, float]:
    """
    See match function docstring. matching concurrently and sorting the result.
    """
    result = {}
    with ProcessPoolExecutor() as executor:
        tasks = {executor.submit(match, movie_time, v): k for k, v in sub_times.items()}
        for task in tqdm(
            as_completed(tasks.keys()),
            desc="Matching Subtitles",
            total=len(sub_times),
            bar_format="{desc}: {bar} {n_fmt}/{total_fmt} {percentage:3.0f}%",
        ):
            result[tasks[task]] = task.result()
    return dict(sorted(result.items(), key=lambda item: item[1], reverse=True))
