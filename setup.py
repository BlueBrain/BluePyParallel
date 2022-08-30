"""Setup for the bluepyparallel package."""
import importlib.util
from pathlib import Path

from setuptools import find_packages
from setuptools import setup

spec = importlib.util.spec_from_file_location(
    "bluepyparallel.version",
    "bluepyparallel/version.py",
)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
VERSION = module.VERSION

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
    "m2r2",
    "sphinx",
    "sphinx-bluebrain-theme",
]

test_reqs = [
    "mpi4py",
    "pytest",
    "pytest-benchmark",
    "pytest-cov",
    "pytest-html",
]

setup(
    name="bluepyparallel",
    author="bbp-ou-cells",
    author_email="bbp-ou-cells@groupes.epfl.ch",
    description="Provides an embarassingly parallel tool with sql backend.",
    long_description=Path("README.md").read_text(encoding="utf-8"),
    long_description_content_type="text/markdown",
    url="https://bbpteam.epfl.ch/documentation/projects/bluepyparallel",
    project_urls={
        "Tracker": "https://bbpteam.epfl.ch/project/issues/projects/CELLS/issues",
        "Source": "https://bbpgitlab.epfl.ch/neuromath/bluepyparallel",
    },
    license="BBP-internal-confidential",
    packages=find_packages(include=["bluepyparallel"]),
    python_requires=">=3.7",
    version=VERSION,
    install_requires=reqs,
    extras_require={
        "docs": doc_reqs,
        "test": test_reqs,
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    include_package_data=True,
)
