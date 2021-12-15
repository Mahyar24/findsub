#! /usr/bin/python3.9

"""
Mahyar@Mahyar24.com, Thu 19 Aug 2021.
"""

from distutils.core import Extension, setup

from Cython.Build import cythonize  # type: ignore

extensions = [
    Extension(name="algo", sources=["./algo.pyx"]),
    # Extension(name="video", sources=["./video.pyx"]),
]

setup(ext_modules=cythonize(extensions))
