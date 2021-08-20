#! /usr/bin/python3.9

"""
This module's goal is to make a data structure for subtitle times
Compatible with python3.9+.
`srt` library is required. -> https://pypi.org/project/srt/
Mahyar@Mahyar24.com, Thu 19 Aug 2021.
"""
import datetime
import os
from concurrent.futures import ALL_COMPLETED, ProcessPoolExecutor, wait

import srt  # type: ignore


def extract_subtitle_time(
    file_name: str,
) -> list[tuple[datetime.timedelta, datetime.timedelta]]:
    """
    Making a data structure for times when there is a dialog.
    ---> [(start1, end1), (start2, end2), ...]
    In case of error, function will catch the exception and return empty list.
    """
    try:
        with open(file_name, "r", encoding="utf-8") as file:
            data = file.read()
        sub = srt.parse(data)
        times = [(item.start, item.end) for item in sub]
    except (UnicodeDecodeError, srt.SRTParseError):
        print(f"Cannot decode {os.path.relpath(file_name)!r}")
        return []
    else:
        return times


def extract_subtitle_times(
    directory: str,
) -> dict[str, list[tuple[datetime.timedelta, datetime.timedelta]]]:
    """
    Making data structure for all subtitles concurrently.
    Check extract_subtitle_time function's docstring.
    """
    subtitles = os.listdir(directory)
    tasks = {}
    with ProcessPoolExecutor() as executor:
        for subtitle in subtitles:
            if subtitle.endswith('.srt'):
                tasks[subtitle] = executor.submit(
                    extract_subtitle_time,
                    os.path.abspath(os.path.join(directory, subtitle)),
                )
        wait(tasks.values(), return_when=ALL_COMPLETED)

    result = {}
    for key, value in tasks.items():
        if val := value.result():
            result[key] = val

    return result
