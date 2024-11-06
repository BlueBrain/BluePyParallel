"""Test the ``bluepyparallel.parallel`` module."""

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

# pylint: disable=missing-function-docstring
# pylint: disable=redefined-outer-name
import importlib.metadata
import json
import subprocess
import sys
from collections.abc import Iterator
from copy import deepcopy

import pandas as pd
import pytest
import yaml
from packaging.version import Version

from bluepyparallel import init_parallel_factory
from bluepyparallel.parallel import DaskDataFrameFactory

dask_version = Version(importlib.metadata.version("dask"))


def _evaluation_function_range(element, coeff_a=1.0, coeff_b=1.0):
    """Mock evaluation function."""
    return element * coeff_a + coeff_b


def _evaluation_function_dict(element, coeff_a=1.0, coeff_b=1.0):
    """Mock evaluation function."""
    return element["a"] * coeff_a + element["b"] * coeff_b


@pytest.fixture
def int_data():
    """Fixture for simple integer data range."""
    return iter(range(10))


@pytest.fixture
def dict_data():
    """Fixture for simple dict data."""
    return [{"a": i, "b": i * i} for i in range(10)]


@pytest.fixture(params=["range", "dict"])
def data(request, int_data, dict_data):
    """Fixture for simple data depending of the type (range or dict)."""
    if request.param == "range":
        return deepcopy(int_data), _evaluation_function_range
    elif request.param == "dict":
        return deepcopy(dict_data), _evaluation_function_dict
    else:
        raise ValueError(f"Unknown value '{request.param}'")


def expected_results(data, func, *args, **kwargs):
    """Fixture with expected results."""
    return [func(i, *args, **kwargs) for i in data]


@pytest.fixture
def func_args_kwargs():
    """Fixture with args and kwargs passed to the evaluated function."""
    return [
        ([], {}),
        ([10.0], {}),
        ([], {"coeff_b": 5.0}),
        ([20.0, 15.0], {}),
        ([30.0], {"coeff_b": 25.0}),
        ([], {"coeff_a": 40.0, "coeff_b": 35.0}),
    ]


class TestFactories:
    """Test the ``bluepyparallel.parallel`` functions."""

    def test_computation(self, data, parallel_factory, func_args_kwargs):
        """Test evaluator on a trivial example."""
        input_data, evaluation_function = data
        if isinstance(input_data, Iterator):
            copied_input = list(input_data)
            with_iter = True
        else:
            copied_input = input_data
            with_iter = False

        for args, kwargs in func_args_kwargs:
            expected_result = expected_results(copied_input, evaluation_function, *args, **kwargs)

            mapper = parallel_factory.get_mapper()
            mapped_data = copied_input if not with_iter else iter(copied_input)

            if isinstance(parallel_factory, DaskDataFrameFactory):
                if isinstance(copied_input[0], dict):
                    name = "name"
                else:
                    name = 0
                meta = pd.DataFrame({name: pd.Series(dtype="object")})
                res = list(mapper(evaluation_function, mapped_data, *args, meta=meta, **kwargs))
                res = pd.concat(res)
                res = res.iloc[:, 0].tolist()
            else:
                res = sorted(mapper(evaluation_function, mapped_data, *args, **kwargs))

            assert res == expected_result

    def test_bad_factory_name(self):
        """Test a factory with a wrong name."""
        with pytest.raises(KeyError):
            init_parallel_factory("UNKNOWN FACTORY")


@pytest.fixture(params=[True, False])
def env_tmpdir(tmpdir, request):
    if request.param:
        dask_tmpdir = str(tmpdir / "tmpdir_from_env")
        yield dask_tmpdir
    else:
        yield None


@pytest.fixture(params=[True, False])
def env_daskconfig(tmpdir, request):
    if request.param:
        # Create dask config file
        dask_config = {"distributed": {"worker": {"memory": {"pause": 0.123456}}}}
        filepath = str(tmpdir / "dask_config.yml")
        with open(filepath, "w", encoding="utf-8") as file:
            yaml.dump(dask_config, file)

        yield filepath
    else:
        yield None


@pytest.mark.parametrize(
    "dask_config",
    [
        pytest.param(None, id="No Dask config"),
        pytest.param({"temporary-directory": "tmpdir"}, id="Dask config with tmp dir"),
    ],
)
@pytest.mark.parametrize(
    "factory_type",
    [
        pytest.param("dask", id="Dask"),
        pytest.param("dask_dataframe", id="Dask-dataframe"),
    ],
)
@pytest.mark.skipif(dask_version < Version("2023.4"), reason="Requires dask >= 2023.4")
def test_dask_config(tmpdir, dask_config, factory_type, env_tmpdir, env_daskconfig):
    """Test the methods to update dask configuration."""
    dask_config_tmpdir = str(tmpdir / "tmpdir_from_config")
    has_tmpdir = (
        dask_config is not None and dask_config.get("temporary-directory", None) is not None
    )
    if has_tmpdir:
        dask_config["temporary-directory"] = dask_config_tmpdir
    dask_config_str = "None" if dask_config is None else json.dumps(dask_config)

    # Must test using a subprocess because the DASK_CONFIG environment variable is only considered
    # when dask is imported
    code = """if True:  # This is just to avoid indentation issue
    import os

    import dask.config
    import dask.distributed

    from bluepyparallel import init_parallel_factory
    from bluepyparallel.parallel import DaskDataFrameFactory
    from bluepyparallel.parallel import DaskFactory


    dask_cluster = dask.distributed.LocalCluster(dashboard_address=None)

    has_tmpdir = {has_tmpdir}
    dask_config_tmpdir = "{tmpdir}"
    env_tmpdir = os.getenv("TMPDIR", None)
    dask_config = {dask_config}
    env_daskconfig = os.getenv("DASK_CONFIG", None)

    print("Values in subprocess:")
    print("tmpdir:", dask_config_tmpdir)
    print("has_tmpdir:", has_tmpdir)
    print("env_tmpdir:", env_tmpdir)
    print("env_daskconfig:", env_daskconfig)
    print("dask_config:", dask_config)

    factory_kwargs = {{
        "address": dask_cluster,
        "dask_config": dask_config,
    }}

    factory = init_parallel_factory("{factory_type}", **factory_kwargs)

    print("tmpdir in dask.config:", dask.config.get("temporary-directory"))
    print(
        "distributed.worker.memory.pause in dask.config:",
        dask.config.get("distributed.worker.memory.pause"),
    )

    if "{factory_type}" == "dask":
        assert isinstance(factory, DaskFactory)
    else:
        assert isinstance(factory, DaskDataFrameFactory)

    if env_daskconfig is not None:
        assert dask.config.get("distributed.worker.memory.pause") == 0.123456
    else:
        assert dask.config.get("distributed.worker.memory.pause") == 0.8

    if has_tmpdir:
        assert dask.config.get("temporary-directory") == dask_config_tmpdir
    else:
        if env_tmpdir is not None:
            assert dask.config.get("temporary-directory") == env_tmpdir
        else:
            assert dask.config.get("temporary-directory") is None
    """.format(
        dask_config=dask_config_str,
        factory_type=factory_type,
        tmpdir=dask_config_tmpdir,
        has_tmpdir=has_tmpdir,
    )
    envs = {}
    if env_daskconfig is not None:
        envs["DASK_CONFIG"] = env_daskconfig
    if env_tmpdir is not None:
        envs["TMPDIR"] = env_tmpdir
    subprocess.check_call([sys.executable, "-c", code], env=envs)
