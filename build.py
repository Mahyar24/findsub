#! /usr/bin/python3.9

"""
Mahyar@Mahyar24.com, Thu 19 Aug 2021.
"""


from distutils.command.build_ext import build_ext
from distutils.core import Extension

from Cython.Build import cythonize

ext_modules = cythonize(
    [
        Extension(
            name="algo",
            include_dirs=["findsub/core"],
            sources=["findsub/core/algo.pyx"],
        ),
    ]
)


class BuildFailed(Exception):
    pass


class ExtBuilder(build_ext):
    def run(self):
        try:
            super().run()
        except (DistutilsPlatformError, FileNotFoundError):
            raise BuildFailed("File not found. Could not compile Cython extensions.")

    def build_extension(self, ext):
        try:
            super().build_extension(ext)
        except (CCompilerError, DistutilsExecError, DistutilsPlatformError, ValueError):
            raise BuildFailed("Could not compile Cython extensions.")


def build(setup_kwargs):
    """
    This function is mandatory in order to build the extensions.
    """
    setup_kwargs.update(
        {"ext_modules": ext_modules, "cmdclass": {"build_ext": ExtBuilder}}
    )
