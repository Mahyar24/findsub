#! /usr/bin/python3.9

"""
This module's goal is to download all subtitles of a suggested movie title
in a specific language from Subscene site.
Compatible with python3.9+.
`cloudscraper` library is required. -> https://pypi.org/project/cloudscraper/
`beautifulsoup4` library is required. -> https://pypi.org/project/beautifulsoup4/
`lxml` library is required. -> https://pypi.org/project/lxml/
`tqdm` library is required. -> https://pypi.org/project/tqdm/
Mahyar@Mahyar24.com, Thu 19 Aug 2021.
"""

import os
import shutil
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Optional

import cloudscraper  # type: ignore
from bs4 import BeautifulSoup  # type: ignore
from tqdm import tqdm  # type: ignore

from .movie import Movie


class Downloader:
    """
    Download Subtitles from subscene.
    """

    SUBSCENE_URL = "https://subscene.com"

    def __init__(
        self,
        movie: Movie,
        lang: str,
        link: Optional[str] = None,
    ) -> None:
        self.lang = lang
        self.link = link
        self.movie = movie

    def suggest_link(self) -> None:
        """
        based on `filename.py` module. (see module's docstring)
        Return title and suggested Subscene link; If it fails for getting title,
        it will raise a ValueError.
        """
        try:
            name, year = self.movie.search()
        except ValueError as error:
            raise ValueError("IMDB API cannot find the name of this movie.") from error
        else:
            subscene_link = (
                self.SUBSCENE_URL
                + f"""/subtitles/{name.replace(":", "").replace(" ", "-")
                .replace("'", "").lower()}"""
            )
            self.link = subscene_link

            print(f"IMDB Search: {name!r} ({year}). Subscene link: {self.link!r}")

    def get_content(self) -> str:
        """
        Get HTML of a link. It will raise a ValueError if respond wasn't ok.
        """
        with cloudscraper.create_scraper() as session:
            with session.get(self.link) as resp:  # type: ignore
                if resp.ok:
                    return resp.text
                raise ValueError(
                    f"Cannot find: {self.link!r}: {resp.status_code!r}\n"
                    f"Please Specify the subscene link of this movie "
                    f"explicitly with help of -s/--subscene option."
                )

    def get_subtitles_links(self) -> list[str]:
        """
        Scraping Subscene page and return a list os subtitle download pages
        with corresponding language.
        """
        content = self.get_content()
        soup = BeautifulSoup(content, "lxml")
        links: list[str] = []
        for html_link in soup.find_all("a"):
            if rf"/{self.lang}/" in html_link["href"]:
                links.append(self.SUBSCENE_URL + html_link["href"])
        if not links:
            raise NotImplementedError(f"No subtitle with {self.lang!r} language found!")
        return links

    def extract_dl_link(
        self, link: str, session: cloudscraper.Session
    ) -> Optional[str]:
        """
        Return download link from Subscene download page.
        """
        with session.get(link) as resp:
            if resp.ok:
                content = resp.text
                soup = BeautifulSoup(content, "lxml")
                download_button = soup.find("a", {"id": "downloadButton"})
                return self.SUBSCENE_URL + download_button["href"]
        return None

    @staticmethod
    def download_one(
        link: str,
        name: str,
        directory: Path,
        session: cloudscraper.Session,
    ) -> Optional[str]:
        """
        Download the subtitle, if response was not okay, return None.
        """
        with session.get(link) as resp:
            if resp.ok:
                with open(directory / name, "wb") as file:
                    for chunk in resp.iter_content(chunk_size=1024):
                        file.write(chunk)
                return name
        return None

    def download_all(self, links: list[str], directory: Path) -> list[str]:
        """
        Extract download links of subtitles and download them.
        """
        num = 0
        with cloudscraper.create_scraper() as session:
            extracting_download_links = [
                self.extract_dl_link(link, session) for link in links
            ]
            with ThreadPoolExecutor() as executor:
                downloads = {}
                for download_link in extracting_download_links:
                    num += 1
                    name = f"{num}.zip"
                    task = executor.submit(
                        self.download_one,
                        download_link,
                        name,
                        directory,
                        session,
                    )
                    downloads[task] = name

                results = []
                for future in tqdm(
                    as_completed(downloads),
                    desc="Downloading Subtitles",
                    total=len(links),
                    bar_format="{desc}: {bar} {n_fmt}/{total_fmt} {percentage:3.0f}%",
                ):
                    if (res := future.result()) is not None:
                        results.append(res)

        return results

    def download(self) -> Path:
        """
        Main download entry point. It will make a directory with movie title (hidden) and cd to it.
        download the files and return list of their filenames and directory path.
        """
        directory = self.movie.dir / f".{self.movie.filename_hash}"

        if directory.is_dir():
            shutil.rmtree(directory)

        os.mkdir(directory)

        if self.link is None:
            self.suggest_link()

        links = self.get_subtitles_links()
        self.download_all(links, directory)

        return directory
