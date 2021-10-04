from distutils.core import Extension, setup

from Cython.Build import cythonize

extensions = [
              Extension(name="algo", sources=["./algo.pyx"]),
             ]

setup(ext_modules=cythonize(extensions))
