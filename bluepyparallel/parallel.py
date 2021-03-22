"""Parallel helper."""
import logging
import multiprocessing
import os
from abc import abstractmethod
from collections.abc import Iterator
from functools import partial
from multiprocessing.pool import Pool

import numpy as np

try:
    import dask.distributed
    import dask_mpi

    dask_available = True
except ImportError:
    dask_available = False

try:
    import ipyparallel

    ipyparallel_available = True
except ImportError:
    ipyparallel_available = False


L = logging.getLogger(__name__)


class ParallelFactory:
    """Abstract class that should be subclassed to provide parallel functions."""

    _BATCH_SIZE = "PARALLEL_BATCH_SIZE"
    _CHUNK_SIZE = "PARALLEL_CHUNK_SIZE"

    # pylint: disable=unused-argument
    def __init__(self, batch_size=None, chunk_size=None):
        self.batch_size = batch_size or int(os.getenv(self._BATCH_SIZE, "0")) or None
        L.info("Using %s=%s", self._BATCH_SIZE, self.batch_size)

        self.chunk_size = batch_size or int(os.getenv(self._CHUNK_SIZE, "0")) or None
        L.info("Using %s=%s", self._CHUNK_SIZE, self.chunk_size)

        if not hasattr(self, "nb_processes"):
            self.nb_processes = 1

    def __del__(self):
        """Call the shutdown method."""
        self.shutdown()

    @abstractmethod
    def get_mapper(self, batch_size=None, chunk_size=None, **kwargs):
        """Return a mapper function that can be used to execute functions in parallel."""

    def shutdown(self):
        """Can be used to cleanup."""

    def _with_batches(self, mapper, func, iterable, batch_size=None):
        """Wrapper on mapper function creating batches of iterable to give to mapper.

        The batch_size is an int corresponding to the number of evaluation in each batch/
        """
        if isinstance(iterable, Iterator):
            iterable = list(iterable)

        batch_size = batch_size or self.batch_size
        if batch_size is not None:
            iterables = [
                _iterable.tolist()
                for _iterable in np.array_split(
                    iterable, len(iterable) // min(batch_size, len(iterable))
                )
            ]
        else:
            iterables = [iterable]

        for _iterable in iterables:
            yield from mapper(func, _iterable)

    def _chunksize_to_kwargs(self, chunk_size, kwargs, label="chunk_size"):
        chunk_size = chunk_size or self.chunk_size
        if chunk_size is not None:
            kwargs[label] = chunk_size


class NoDaemonProcess(multiprocessing.Process):
    """Class that represents a non-daemon process"""

    # pylint: disable=dangerous-default-value

    def __init__(self, group=None, target=None, name=None, args=(), kwargs={}):
        """Ensures group=None, for macosx."""
        super().__init__(group=None, target=target, name=name, args=args, kwargs=kwargs)

    def _get_daemon(self):  # pylint: disable=no-self-use
        """Get daemon flag"""
        return False

    def _set_daemon(self, value):
        """Set daemon flag"""

    daemon = property(_get_daemon, _set_daemon)


class NestedPool(Pool):  # pylint: disable=abstract-method
    """Class that represents a MultiProcessing nested pool"""

    Process = NoDaemonProcess


class SerialFactory(ParallelFactory):
    """Factory that do not work in parallel."""

    def get_mapper(self, batch_size=None, chunk_size=None, **kwargs):
        """Get a map."""
        return map


class MultiprocessingFactory(ParallelFactory):
    """Parallel helper class using multiprocessing."""

    _CHUNKSIZE = "PARALLEL_CHUNKSIZE"

    def __init__(self, batch_size=None, chunk_size=None, processes=None, **kwargs):
        """Initialize multiprocessing factory."""

        super().__init__(batch_size, chunk_size)

        self.nb_processes = processes or os.cpu_count()
        self.pool = NestedPool(processes=self.nb_processes, **kwargs)

    def get_mapper(self, batch_size=None, chunk_size=None, **kwargs):
        """Get a NestedPool."""
        self._chunksize_to_kwargs(chunk_size, kwargs, label="chunksize")

        def _mapper(func, iterable):
            return self._with_batches(
                partial(self.pool.imap_unordered, **kwargs),
                func,
                iterable,
            )

        return _mapper

    def shutdown(self):
        """Close the pool."""
        self.pool.close()


class IPyParallelFactory(ParallelFactory):
    """Parallel helper class using ipyparallel."""

    _IPYTHON_PROFILE = "IPYTHON_PROFILE"

    def __init__(self, batch_size=None, chunk_size=None, profile=None, **kwargs):
        """Initialize the ipyparallel factory."""
        profile = profile or os.getenv(self._IPYTHON_PROFILE, None)
        L.debug("Using %s=%s", self._IPYTHON_PROFILE, profile)
        self.rc = ipyparallel.Client(profile=profile, **kwargs)
        self.nb_processes = len(self.rc.ids)
        self.lview = self.rc.load_balanced_view()
        super().__init__(batch_size, chunk_size)

    def get_mapper(self, batch_size=None, chunk_size=None, **kwargs):
        """Get an ipyparallel mapper using the profile name provided."""
        if "ordered" not in kwargs:
            kwargs["ordered"] = False

        self._chunksize_to_kwargs(chunk_size, kwargs)

        def _mapper(func, iterable):
            return self._with_batches(
                partial(self.lview.imap, **kwargs), func, iterable, batch_size=batch_size
            )

        return _mapper

    def shutdown(self):
        """Remove zmq."""
        if self.rc is not None:
            self.rc.close()


class DaskFactory(ParallelFactory):
    """Parallel helper class using dask."""

    _SCHEDULER_PATH = "PARALLEL_DASK_SCHEDULER_PATH"

    def __init__(
        self, batch_size=None, chunk_size=None, scheduler_file=None, address=None, **kwargs
    ):
        """Initialize the dask factory."""
        dask_scheduler_path = scheduler_file or os.getenv(self._SCHEDULER_PATH)
        self.interactive = True
        if dask_scheduler_path:
            L.info("Connecting dask_mpi with scheduler %s", dask_scheduler_path)
        if address:
            L.info("Connecting dask_mpi with address %s", address)
        if not dask_scheduler_path and not address:
            self.interactive = False
            L.info("Starting dask_mpi...")
            dask_mpi.initialize()
        self.client = dask.distributed.Client(
            address=address,
            scheduler_file=dask_scheduler_path,
            **kwargs,
        )
        self.nb_processes = len(self.client.scheduler_info()["workers"])
        super().__init__(batch_size, chunk_size)

    def shutdown(self):
        """Close the scheduler and the cluster if it was created by the factory."""
        cluster = self.client.cluster
        self.client.close()
        if not self.interactive:
            cluster.close()

    def get_mapper(self, batch_size=None, chunk_size=None, **kwargs):
        """Get a Dask mapper."""
        self._chunksize_to_kwargs(chunk_size, kwargs, label="batch_size")

        def _mapper(func, iterable):
            def _dask_mapper(func, iterable):
                futures = self.client.map(func, iterable, **kwargs)
                for _future, result in dask.distributed.as_completed(futures, with_results=True):
                    yield result

            return self._with_batches(_dask_mapper, func, iterable, batch_size=batch_size)

        return _mapper


def init_parallel_factory(parallel_lib, *args, **kwargs):
    """Return the desired instance of the parallel factory.

    The main factories are:

    * None: return a serial mapper (the standard :func:`map` function).
    * multiprocessing: return a mapper using the standard :mod:`multiprocessing`.
    * dask: return a mapper using the :class:`distributed.Client`.
    * ipyparallel: return a mapper using the :mod:`ipyparallel` library.
    """
    parallel_factories = {
        None: SerialFactory,
        "multiprocessing": MultiprocessingFactory,
    }
    if dask_available:
        parallel_factories["dask"] = DaskFactory
    if ipyparallel_available:
        parallel_factories["ipyparallel"] = IPyParallelFactory

    try:
        parallel_factory = parallel_factories[parallel_lib](*args, **kwargs)
    except KeyError:
        L.critical(
            "The %s factory is not available, maybe the required libraries are not properly "
            "installed.",
            parallel_lib,
        )
        raise
    L.info("Initialized %s factory", parallel_lib)
    return parallel_factory
