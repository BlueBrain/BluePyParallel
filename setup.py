"""Setup for the bluepyparallel package."""
import importlib.util
from pathlib import Path

from setuptools import find_namespace_packages
from setuptools import setup

spec = importlib.util.spec_from_file_location(
    "bluepyparallel.version",
    "bluepyparallel/version.py",
)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
VERSION = module.VERSION

reqs = [
    "pandas>=1.3",
    "ipyparallel>=6.3,<7",
    "dask[dataframe, distributed]>=2021.11",
    "dask-mpi>=2021.11",
    "distributed>=2021.11",
    "sqlalchemy>=1.4.24",
    "sqlalchemy<2; python_version<'3.8'",
    "sqlalchemy-utils>=0.37.2",
    "tqdm>=3.7",
]

doc_reqs = [
    "m2r2",
    "sphinx",
    "sphinx-bluebrain-theme",
]

test_reqs = [
    "mpi4py>=3.0.1",
    "packaging>=20",
    "pytest>=6.1",
    "pytest-benchmark>=3.4",
    "pytest-cov>=3",
    "pytest-html>=3.1",
]

setup(
    name="bluepyparallel",
    author="bbp-ou-cells",
    author_email="bbp-ou-cells@groupes.epfl.ch",
    description="Provides an embarrassingly parallel tool with sql backend.",
    long_description=Path("README.md").read_text(encoding="utf-8"),
    long_description_content_type="text/markdown",
    url="https://bbpteam.epfl.ch/documentation/projects/bluepyparallel",
    project_urls={
        "Tracker": "https://bbpteam.epfl.ch/project/issues/projects/CELLS/issues",
        "Source": "https://bbpgitlab.epfl.ch/neuromath/bluepyparallel",
    },
    license="BBP-internal-confidential",
    packages=find_namespace_packages(include=["bluepyparallel*"]),
    python_requires=">=3.8",
    version=VERSION,
    install_requires=reqs,
    extras_require={
        "docs": doc_reqs,
        "test": test_reqs,
    },
    include_package_data=True,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
    ],
)
