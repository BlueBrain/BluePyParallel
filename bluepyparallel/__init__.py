"""BluePyParallel package.

Provides an embarrassingly parallel tool with sql backend.
"""
import importlib.metadata

from bluepyparallel.evaluator import evaluate  # noqa
from bluepyparallel.parallel import init_parallel_factory  # noqa

__version__ = importlib.metadata.version("BluePyParallel")
