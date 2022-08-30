"""bluepyparallel package.

Provides an embarassingly parallel tool with sql backend.
"""
from bluepyparallel.evaluator import evaluate  # noqa
from bluepyparallel.parallel import init_parallel_factory  # noqa
from bluepyparallel.version import VERSION as __version__  # noqa
