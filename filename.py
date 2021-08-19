#! /usr/bin/python3.9

"""
This module's goal is to get a movie filename, clean it, and by using IMDB api return the
official title of movie.
Compatible with python3.9+.
`IMDbPY` library is required. -> https://pypi.org/project/IMDbPY/
In case of failure, it will raise a ValueError.
Mahyar@Mahyar24.com, Thu 19 Aug 2021.
"""

import string
from datetime import date

from imdb import IMDb  # type: ignore

IMDB = IMDb()


def find_separator(name: str) -> str:
    """
    Checking for most used punctuation or whitespace to suggest it as separator.
    """
    separators = frozenset(string.punctuation + string.whitespace)
    occurrences = []
    for character in separators:
        occurrences.append((character, name.count(character)))
    suggested_separator = max(occurrences, key=lambda x: x[1])[0]
    return suggested_separator


def find_year(name: list[str]) -> str:
    """
    Checking for existence of year in filename. if none, '' will return.
    """
    for part in name:
        if part.isdigit():
            if date.today().year >= int(part) >= 1890:  # Sensible year for a movie.
                return part
    return ""


def clean_file_name(file_name: str) -> str:  # TODO: add support for series too!
    """
    We have an assumption that file names are in this kind of patterns:
        'Borat.Subsequent.Moviefilm.2020.1080p.WEB-DL.RARBG.DigiMoviez.mkv'
        'Hellboy II The Golden Army 2008 720p (MarzFun.ir).mp4'
    NO series support yet!
    """
    file_name = file_name[: file_name.rfind(".")]  # Removing mime.
    suggested_separator = find_separator(file_name)
    file_name_split = file_name.split(suggested_separator)
    suggested_year = find_year(file_name_split)
    if suggested_year:
        return (
            " ".join(file_name_split[: file_name_split.index(suggested_year)])
            + f" ({suggested_year})"
        )
    name = []
    for part in file_name_split:
        if part.replace(r"'", "").isalpha():
            name.append(part)
        else:
            break
    return " ".join(name)


def imdb_search(name: str) -> str:
    """
    Based on a clean name, search in IMDB api for title. raise ValueError if nothing pop out.
    """
    result = IMDB.search_movie(name)
    if result:
        suggested_movie = result[0]
        return suggested_movie.data["title"]
    raise ValueError(f"Bad name: {name!r}")


def process(file_name: str) -> str:
    """
    Clean the name and search in IMDB, raise ValueError if something goes wrong.
    """
    name = clean_file_name(file_name)
    if name:
        title = imdb_search(name)
        return title
    raise ValueError("Cannot clean the name!")
