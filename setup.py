"""Setup for the BluePyParallel package."""
import imp

from setuptools import find_packages
from setuptools import setup

# Read the contents of the README file
with open("README.rst", encoding="utf-8") as f:
    README = f.read()

reqs = [
    "pandas",
    "ipyparallel<7",
    "dask[dataframe, distributed]>=2.30",
    "dask-mpi>=2.20",
    "sqlalchemy>1.4",
    "sqlalchemy-utils",
    "tqdm",
]

doc_reqs = [
    "docutils<0.19",  # TODO: Remove this when m2r2>0.3.2 is released
    "m2r2",
    "sphinx<4",
    "sphinx-bluebrain-theme",
]

VERSION = imp.load_source("", "bluepyparallel/version.py").VERSION

setup(
    name="bluepyparallel",
    author="bbp-ou-cells",
    author_email="bbp-ou-cells@groupes.epfl.ch",
    version=VERSION,
    description="Provides an embarassingly parallel tool with sql backend",
    long_description=README,
    long_description_content_type="text/x-rst",
    url="https://bbpteam.epfl.ch/documentation/projects/BluePyParallel",
    project_urls={
        "Tracker": "https://bbpteam.epfl.ch/project/issues/projects/CELLS/issues",
        "Source": "https://bbpgitlab.epfl.ch/neuromath/bluepyparallel",
    },
    license="BBP-internal-confidential",
    install_requires=reqs,
    extras_require={
        "docs": doc_reqs,
    },
    packages=find_packages(exclude=["tests"]),
    python_requires=">=3.7",
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
)
