#! /usr/bin/python3.9

"""
This module's goal is to calculate mutual percentage of time between two data structure
based on `subtitle.py` module. It will show how much they are potentially synchronous.
Compatible with python3.9+.
Mahyar@Mahyar24.com, Thu 19 Aug 2021.
"""

from concurrent.futures import ProcessPoolExecutor, as_completed
from datetime import timedelta

from tqdm import tqdm  # type: ignore


def match(
    base: list[tuple[timedelta, timedelta]],
    other: list[tuple[timedelta, timedelta]],
) -> float:  # TODO: use Cython instead for speed.
    """
    Based on the data structure, calculate that how much of the time that there is
    some speech going on in base, there is a subtitle in other.
    """
    matched = timedelta(0)
    base_total = sum([(item[1] - item[0]).total_seconds() for item in base])
    for dialog in other:
        for speech in base:
            if speech[0] > dialog[1] or dialog[0] > speech[1]:  # Huge SpeedUP.
                continue

            if (
                dialog[0] <= speech[0] and dialog[1] >= speech[1]
            ):  # base is included in other completely
                matched += speech[1] - speech[0]
            elif (
                dialog[0] >= speech[0] and speech[1] >= dialog[1]
            ):  # other is included in base completely
                matched += dialog[1] - dialog[0]
            elif dialog[0] <= speech[0] <= dialog[1] <= speech[1]:  # partially
                matched += dialog[1] - speech[0]
            elif speech[0] <= dialog[0] <= speech[1] <= dialog[1]:  # partially
                matched += speech[1] - dialog[0]

    return matched.total_seconds() / base_total


def match_all(
    movie_time: list[tuple[timedelta, timedelta]],
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
