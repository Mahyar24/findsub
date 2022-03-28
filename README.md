# FindSub

FindSub is an Application for automatically downloading and ranking subtitles based on how much they are synced
from [subscene](https://subscene.com/).
**Compatible With Unix Systems.**


## Installation
Let's assume you are using python3.9 (python3.9+ is supported)
To install finsub, first, you must install these prerequisites:

```bash
sudo apt install gcc python3.9-dev
```
‍‍‍‍‍‍
After that, the recommended way is by using [pipx](https://github.com/pypa/pipx).
to install pipx:

```bash
sudo apt install python3.9-venv pipx
```

Then install FindSub by using the command below:

```bash
pipx install --python python3.9 findsub
```

FFmpeg and FFprobe are also needed for extracting of movie's audio that is in use for most cases.

```bash
sudo apt install ffmpeg
```

P.S: **Bash and Iconv** are required too.

# Basic Usage and explanation. (Must read!)

```bash
findsub The.French.Dispatch.2021.1080p.WEB-DL.x264.6CH-Pahe.FilmBan.mkv
```
→ First, findsub try to guess the name of the movie based on the filename and with the help of IMDB. 
Simultaneously it will extract the movie's audio by using "**FFmpeg**"  and "**FFprobe**". 
If a cached extracted audio is present in the same directory, findsub will skip this stage and use it instead.
At the same time, findsub tries to download the subtitles from subscene in the desired language.
You can use -l/--language to select a language (ISO 639-1). if nothing is specified with this option, 
**findsub will try to use "FINDSUB_LANG" environment variable** and if nothing is set, it will use "En" as default.
Sometimes, especially when the original movie name is not in English, findsub cannot find the paired subscene page, 
and you should manually set the subscene link of the page with the help of -s/--subscene option.


# Advance Usage
## Languages 

```bash
findsub The.French.Dispatch.2021.1080p.WEB-DL.x264.6CH-Pahe.FilmBan.mkv --language "fa";
```
OR
```
export FINDSUB_LANG="fa"; findsub The.French.Dispatch.2021.1080p.WEB-DL.x264.6CH-Pahe.FilmBan.mkv
```
→ With these two approaches, you can set the language.
You must use two-letter codes based on (ISO 639-1). 
P.S.: **exceptionally, use "bz" for Brazillian Portuguese.**

## Speeding up
```bash
findsub The.French.Dispatch.2021.1080p.WEB-DL.x264.6CH-Pahe.FilmBan.mkv --audio ./already_extraced_audio.wav
```
OR
```bash
findsub The.French.Dispatch.2021.1080p.WEB-DL.x264.6CH-Pahe.FilmBan.mkv --synced-subtitle ./synced_sub.srt
```
→ use an already extracted audio or a sync subtitle to speed up the program.
```bash
findsub The.French.Dispatch.2021.1080p.WEB-DL.x264.6CH-Pahe.FilmBan.mkv --subtitles-directory downloaded_sub/
```
→ Skip downloading subtitles and rank the subtitles within the mentioned directory.

## -s/--subscene
```bash
subfinder The_Sea_Inside_2004_720p_BrRip_YIFY.mkv -s https://subscene.com/subtitles/the-sea-inside-mar-adentro
```
→ Sometimes FindSub cannot find the subscene page for a movie, in that case, you should manually pass the link to it.
- check `findsub --help` for more info.


## Issues
Findsub currently doesn't support downloading subtitles for series episodes. 
Also, it may not work very well with windows, but it should be usable.


## Contributing
    Written by: Mahyar Mahdavi <Mahyar@Mahyar24.com>.
    License: GNU GPLv3.
    Source Code: <https://github.com/mahyar24/FindSub>.
    PyPI: <https://pypi.org/project/FindSub/>.
    Reporting Bugs and P.R.s are welcomed. :)

## License
[GPLv3](https://choosealicense.com/licenses/gpl-3.0)
