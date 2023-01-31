"""Test the ``bluepyparallel.parallel`` module."""
# pylint: disable=missing-function-docstring
# pylint: disable=redefined-outer-name
from collections.abc import Iterator
from copy import deepcopy

import pandas as pd
import pytest

from bluepyparallel import init_parallel_factory
from bluepyparallel.parallel import DaskDataFrameFactory


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
        values = deepcopy(int_data), _evaluation_function_range
    elif request.param == "dict":
        values = deepcopy(dict_data), _evaluation_function_dict
    return values


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
                res = res[name].tolist()
            else:
                res = sorted(mapper(evaluation_function, mapped_data, *args, **kwargs))

            assert res == expected_result

    def test_bad_factory_name(self):
        """Test a factory with a wrong name."""
        with pytest.raises(KeyError):
            init_parallel_factory("UNKNOWN FACTORY")
