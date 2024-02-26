"""Configuration for the pytest test suite."""

# Copyright 2021-2024 Blue Brain Project / EPFL

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

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
