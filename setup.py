# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['findsub', 'findsub.core']

package_data = \
{'': ['*'], 'findsub': ['data/*', 'scripts/*']}

install_requires = \
['IMDbPY>=2021.4.18,<2022.0.0',
 'aiofiles>=0.8.0,<0.9.0',
 'aiohttp[speedups]>=3.8.1,<4.0.0',
 'beautifulsoup4>=4.10.0,<5.0.0',
 'lxml>=4.7.1,<5.0.0',
 'srt>=3.5.0,<4.0.0',
 'tqdm>=4.62.3,<5.0.0',
 'webrtcvad>=2.0.10,<3.0.0']

entry_points = \
{'console_scripts': ['finsub = findsub.__main__:run']}

setup_kwargs = {
    'name': 'findsub',
    'version': '0.0.1',
    'description': 'Finding and ranking subtitles from subscene by how much they are sync',
    'long_description': None,
    'author': 'Mahyar Mahdavi',
    'author_email': 'Mahyar@Mahyar24.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}
from build import *
build(setup_kwargs)

setup(**setup_kwargs)
