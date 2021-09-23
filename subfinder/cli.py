#! /usr/bin/python3.9

"""
This module's goal is to parsing the cli options and arguments.
Compatible with python3.9+.
Mahyar@Mahyar24.com, Thu 19 Aug 2021.
"""

import argparse
import json
import os
import textwrap


def find_language(code: str) -> str:
    """
    Reading langs.json and trying to find desired language
    by checking two letter codes base on ISO 639-1.
    """
    with open(
        "/home/mahyar/Works/ShittyStuff/SubFinder/langs.json", encoding="utf-8"
    ) as langs_file:
        langs = json.load(langs_file)

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
            Source Code: <https://github.com/mahyar24/subfinder>.
            Reporting Bugs and PRs are welcomed. :)
            """
        )
    )
    group_link_dir = (
        parser.add_mutually_exclusive_group()
    )  # Link or directory, not both!

    parser.add_argument(
        "file",
        help="Select desired movie.",
    )

    parser.add_argument(
        "-l",
        "--language",
        default="fa",
        help="Two letter code for desired subtitle's language. (ISO 639-1)",
    )

    group_link_dir.add_argument(
        "-s", "--subscene", help="URL of subscene for the movie."
    )

    group_link_dir.add_argument(
        "-d",
        "--subtitles-directory",
        type=os.path.abspath,  # type: ignore # Make it absolute path.
        help="Check matching of subtitles in directory with movie.",
    )

    parser.add_argument(
        "-a",
        "--audio",
        help="If extracted audio is available, use the path to speed up program.",
    )

    return parser.parse_args()
