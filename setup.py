#!/usr/bin/env python

import imp
import sys

from setuptools import setup, find_packages

if sys.version_info < (3, 6):
    sys.exit("Sorry, Python < 3.6 is not supported")

# Read the contents of the README file
with open("README.rst", encoding="utf-8") as f:
    README = f.read()

doc_reqs = [
    "sphinx-bluebrain-theme",
]

VERSION = imp.load_source("", "bluepyparallel/version.py").__version__

setup(
    name="BluePyParallel",
    author="BlueBrain cells",
    author_email="bbp-ou-cells@groupes.epfl.ch",
    version=VERSION,
    description="Provides an embarassingly parallel tool with sql backend",
    long_description=README,
    long_description_content_type="text/x-rst",
    url="https://bbpteam.epfl.ch/documentation/projects/BluePyParallel",
    project_urls={
        "Tracker": "https://bbpteam.epfl.ch/project/issues/projects/CELLS/issues",
        "Source": "ssh://bbpcode.epfl.ch/cells/BluePyParallel",
    },
    license="BBP-internal-confidential",
    install_requires=[
        "pandas",
        "ipyparallel",
        "dask[distributed]>=2.30",
        "dask-mpi>=2.20",
        "tqdm",
    ],
    extras_require={
        "docs": doc_reqs,
    },
    packages=find_packages(exclude=["tests"]),
)
