#! /usr/bin/python3.9

"""
This module's goal is parsing the cli options and arguments.
Compatible with python3.9+.
Mahyar@Mahyar24.com, Thu 19 Aug 2021.
"""

import argparse
import json
import os
import pathlib
import pkgutil
import textwrap


def find_language(code: str) -> str:
    """
    Reading langs.json and trying to find desired language
    by checking two-letter codes base on ISO 639-1.
    Additionally, "bz" -> "brazillian-portuguese".
    """
    if (langs_file := pkgutil.get_data(__name__, "data/langs.json")) is None:
        raise FileNotFoundError("langs.json does not exist")

    langs = json.loads(langs_file.decode("utf-8"))

    for key, value in langs.items():
        if code.lower() == key:
            result = value["name"].split()[0]
            print(f'{code!r} -> {value["name"]!r}.')
            return result.lower()

    raise ValueError(f"{code!r} not found!")


def parsing_args() -> argparse.Namespace:
    """
    Parsing the passed arguments, read help (-h, --help) for further information.
    """
    parser = argparse.ArgumentParser(
        epilog=textwrap.dedent(
            """
            Written by: Mahyar Mahdavi <Mahyar@Mahyar24.com>.
            Source Code: <https://github.com/mahyar24/findsub>.
            PyPI: <https://pypi.org/project/findsub/>
            Reporting Bugs and PRs are welcomed. :)
            """
        )
    )
    group_link_dir = (
        parser.add_mutually_exclusive_group()
    )  # Link or directory, not both!

    parser.add_argument(
        "file", help="Select desired movie.", type=lambda x: pathlib.Path(x).absolute()
    )

    parser.add_argument(
        "-l",
        "--language",
        default=os.environ.get("FINDSUB_LANG", "en"),
        type=find_language,
        help="Two letter code for desired subtitle's language. (ISO 639-1) [Additionally: 'bz' -> "
        "'brazillian-portuguese']",
    )

    group_link_dir.add_argument(
        "-s", "--subscene", help="URL of subscene for the movie."
    )

    group_link_dir.add_argument(
        "-d",
        "--subtitles-directory",
        type=lambda x: pathlib.Path(x).absolute(),
        help="Check against already present subtitles in a directory.",
    )

    parser.add_argument(
        "-b",
        "--synced-subtitle",
        type=lambda x: pathlib.Path(x).absolute(),
        help="If you already have a synced subtitle, use it as base. (alot faster)",
    )

    parser.add_argument(
        "-a",
        "--audio",
        type=lambda x: pathlib.Path(x).absolute(),
        help="If extracted audio is available, use the path to it to speed up the program.",
    )

    return parser.parse_args()
