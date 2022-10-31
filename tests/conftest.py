"""Configuration for the pytest test suite."""
# pylint: disable=redefined-outer-name
import copy
import os

import dask.distributed
import pytest

from bluepyparallel import init_parallel_factory


@pytest.fixture
def db_url(tmpdir):
    """The DB URL."""
    return tmpdir / "db.sql"


@pytest.fixture(params=[None, "multiprocessing", "ipyparallel", "dask", "dask_dataframe"])
def factory_type(request):
    """The factory type."""
    return request.param


@pytest.fixture(scope="session")
def dask_cluster():
    """The dask cluster."""
    cluster = dask.distributed.LocalCluster(dashboard_address=None)
    yield cluster
    cluster.close()


@pytest.fixture(
    params=[
        {},
        {"chunk_size": 2},
        {"batch_size": 2},
        {"chunk_size": 2, "batch_size": 2},
        {"chunk_size": 999, "batch_size": 999},
    ]
)
def parallel_factory(factory_type, dask_cluster, request):
    """The parallel factory."""
    factory_kwargs = copy.deepcopy(request.param)
    if factory_type in ["dask", "dask_dataframe"]:
        factory_kwargs["address"] = dask_cluster
    elif factory_type == "ipyparallel":
        tox_name = os.environ.get("TOX_ENV_NAME")
        if tox_name:
            factory_kwargs["cluster_id"] = f"bluepyparallel_{tox_name}"
    return init_parallel_factory(factory_type, **factory_kwargs)
