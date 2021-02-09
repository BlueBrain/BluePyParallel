#!/usr/bin/env python

import imp
import sys

from setuptools import setup, find_packages

if sys.version_info < (3, 6):
    sys.exit("Sorry, Python < 3.6 is not supported")

VERSION = imp.load_source("", "bluepyparallel/version.py").__version__

setup(
    name="BluePyParallel",
    author="BlueBrain cells",
    author_email="bbp-ou-cell@groupes.epfl.ch",
    version=VERSION,
    description="",
    license="BBP-internal-confidential",
    install_requires=[
        "pandas",
        "ipyparallel",
        "dask[distributed]>=2.30",
        "dask_mpi>=2.20",
        "tqdm",
    ],
    packages=find_packages(),
)
