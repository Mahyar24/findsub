#! /usr/bin/python3.9

"""
This module's goal is to get a movie filename, clean it, and by using IMDB api return the
official title of movie.
Compatible with python3.9+.
`IMDbPY` library is required. -> https://pypi.org/project/IMDbPY/
In case of failure, it will raise a ValueError.
Compatible with python3.9+.
Mahyar@Mahyar24.com, Thu 19 Aug 2021.
"""

import pathlib
import string
from datetime import date
from hashlib import md5

from imdb import IMDb  # type: ignore


class Movie:
    """
    Creating an instance of movie and process the data of it base on IMDB API.
    """

    def __init__(self, file: pathlib.Path) -> None:
        self.path = file.absolute()
        self.filename = self.path.name
        self.filename_only = self.path.stem
        self.mime = self.path.suffix
        self.dir = self.path.parent.absolute()
        self.filename_hash = md5(self.filename.encode("utf-8")).hexdigest()
        self.suggested_separator = "."
        self.suggested_year = ""
        self.imdb = IMDb()

    def _find_separator(self) -> str:
        """
        Checking for most used punctuation or whitespace to suggest it as separator.
        """
        separators = frozenset(string.punctuation + string.whitespace)
        occurrences = []
        for character in separators:
            occurrences.append((character, self.filename_only.count(character)))
        return max(occurrences, key=lambda x: x[1])[0]

    @staticmethod
    def _find_year(split_filename: list[str]) -> str:
        """
        Checking for existence of year in filename. if none, '' will return.
        """
        for part in split_filename:
            if part.isdigit():
                if date.today().year >= int(part) >= 1890:  # Sensible year for a movie.
                    return part
        return ""

    def clean_filename(self) -> str:
        """
        We have an assumption that file names are in this kind of patterns:
            'Borat.Subsequent.Moviefilm.2020.1080p.WEB-DL.RARBG.DigiMoviez.mkv'
            'Hellboy II The Golden Army 2008 720p (MarzFun.ir).mp4'
        NO series support yet!
        """
        self.suggested_separator = self._find_separator()
        split_filename = self.filename_only.split(self.suggested_separator)
        self.suggested_year = self._find_year(split_filename)
        if self.suggested_year:
            result = (
                " ".join(split_filename[: split_filename.index(self.suggested_year)])
                + f" ({self.suggested_year})"
            )
        else:
            name = []
            for part in split_filename:
                if part.replace(r"'", "").isalpha():
                    name.append(part)
                else:
                    break
            result = " ".join(name)

        if result:
            return result
        raise ValueError(f"Cannot clean the {self.filename_only}!")

    def search(self) -> tuple[str, str]:
        """
        Based on a clean name, search in IMDB api for title. raise ValueError if nothing pop out.
        """
        clean_filename = self.clean_filename()
        result = self.imdb.search_movie(clean_filename)
        if result:
            suggested_movie = result[0]
            return suggested_movie.data["title"], suggested_movie.data["year"]
        raise ValueError(f"Cannot find: {clean_filename!r}")

    def __repr__(self) -> str:
        return f"Movie(Path={self.path!r}, Name={self.filename_only!r})"
