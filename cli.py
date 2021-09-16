#! /usr/bin/python3.9

"""
This module's goal is to parsing the cli options and arguments.
Compatible with python3.9+.
Mahyar@Mahyar24.com, Thu 19 Aug 2021.
"""

import argparse
import os


def parsing_args() -> argparse.Namespace:
    """
    Parsing the passed arguments, read help (-h, --help) for further information.
    """
    parser = argparse.ArgumentParser()
    group_link_dir = (
        parser.add_mutually_exclusive_group()
    )  # Link or directory, not both!

    parser.add_argument(
        "file",
        help="Select desired movie.",
    )

    parser.add_argument(  # TODO: add real language support.
        "-l",
        "--language",
        default="farsi_persian",
        help="Desired language for subtitle.",
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
