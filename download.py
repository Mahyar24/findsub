#! /usr/bin/python3.9

"""
This module's goal is to download all subtitles of a suggested movie title
in a specific language from Subscene site.
Compatible with python3.9+.
`aiofiles` library is required. -> https://pypi.org/project/aiofiles/
`aiohttp` library is required. -> https://pypi.org/project/aiohttp/
`beautifulsoup4` library is required. -> https://pypi.org/project/beautifulsoup4/
Mahyar@Mahyar24.com, Thu 19 Aug 2021.
"""

import asyncio
import os
from typing import Optional

import aiofiles
import aiohttp
from bs4 import BeautifulSoup  # type: ignore

from filename import process

SUBSCENE_URL = "https://subscene.com"


def name_from_link(link: str) -> str:
    """
    Suggest name of the movie by looking at subscene link.
    """
    return link.split(r"/")[-1].replace("-", " ")


def suggest_link(file_name: str) -> tuple[str, str]:
    """
    based on `filename.py` module. (see module's docstring)
    Return title and suggested Subscene link; If it fails for getting title,
    it will raise a ValueError.
    """
    try:
        name = process(file_name)
    except ValueError:
        print(f"Cannot get name of {file_name!r}")
        raise
    else:
        return name, SUBSCENE_URL + "/subtitles/{}".format(
            name.replace(":", "").replace(" ", "-").lower()
        )


async def get_content(link: str) -> str:
    """
    Get HTML of a link. It will raise a ValueError if respond wasn't ok.
    """
    async with aiohttp.ClientSession() as session:
        async with session.get(link) as resp:
            if resp.ok:
                return await resp.text()
            raise ValueError(f"{link!r}: {resp.status!r}")


async def get_all_links(link: str, lang: str) -> list[str]:
    """
    Scraping Subscene page and return a list os subtitle download pages with corresponding language.
    """
    content = await get_content(link)
    soup = BeautifulSoup(content, "lxml")
    links = []
    for html_link in soup.find_all("a"):
        if rf"/{lang}/" in html_link["href"]:
            links.append(SUBSCENE_URL + html_link["href"])
    if not links:
        raise ValueError(f"No subtitle with {lang!r} language found!")
    return links


async def extract_dl_link(
    session: aiohttp.client.ClientSession, link: str
) -> Optional[str]:
    """
    Return download link from Subscene download page.
    """
    async with session.get(link) as resp:
        if resp.ok:
            content = await resp.text()
            soup = BeautifulSoup(content, "lxml")
            download_button = soup.find("a", {"id": "downloadButton"})
            return SUBSCENE_URL + download_button["href"]
    return None


async def download_one(
    session: aiohttp.client.ClientSession, link: str, name: str, directory: str
) -> Optional[str]:
    """
    Download the subtitle, if response was not okay, return None.
    """
    async with session.get(link) as resp:
        if resp.ok:
            async with aiofiles.open(os.path.join(directory, name), "wb") as file:
                while True:
                    chunk = await resp.content.read(1024)
                    if not chunk:
                        break
                    await file.write(chunk)
            return name
    return None


async def download_all(
    session: aiohttp.client.ClientSession, links: list[str], directory: str
) -> list[str]:
    """
    Extract download links of subtitles and download them.
    """
    num = 0
    extracting_download_links = [
        asyncio.create_task(extract_dl_link(session, link)) for link in links
    ]
    downloading_files = []
    for extract_coro in asyncio.as_completed(extracting_download_links):
        download_link = await extract_coro
        if download_link is not None:
            num += 1
            name = f"{num}.zip"
            downloading_files.append(
                asyncio.create_task(
                    download_one(session, download_link, name, directory)
                )
            )
    result = [
        result
        for result in await asyncio.gather(*downloading_files)
        if result is not None
    ]
    return result


async def async_main(name: str, link: str, lang: str) -> tuple[list[str], str]:
    """
    Main async entry point. It will make a directory with movie title (hidden) and cd to it.
    download the files and return list of their filenames and directory path.
    """
    directory = "." + name
    if not os.path.isdir(directory):
        os.mkdir(directory)

    links = await get_all_links(link, lang)
    async with aiohttp.ClientSession() as session:
        zip_files = await download_all(session, links, directory)
    return zip_files, directory


def get_files(
    lang: str,
    file_name: Optional[str] = None,
    link: Optional[str] = None,
) -> tuple[list[str], str]:
    """
    We will use only this function externally. Suggest the link
    and download files and return their filenames and directory path.
    """
    if link is not None:
        subscene_link = link
        movie = name_from_link(link)
    else:
        if file_name is not None:
            movie, subscene_link = suggest_link(file_name)
        else:
            raise ValueError("One of the file_name/link must provided.")
    zip_files, directory = asyncio.run(async_main(movie, subscene_link, lang))
    return zip_files, directory
