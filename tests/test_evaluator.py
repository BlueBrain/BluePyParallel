"""Test the bluepyparallel.evaluator module"""
# pylint: disable=redefined-outer-name
import time
from copy import deepcopy

import numpy as np
import pandas as pd
import pytest
from pandas._testing import assert_frame_equal

from bluepyparallel import evaluate
from bluepyparallel import init_parallel_factory


def _evaluation_function(row, factor=10.0, coeff=0.0):
    """Mock evaluation function."""
    return {"result_orig": row["value"], "result_10": factor * row["value_1"] + coeff}


def _slow_function(*args, **kwargs):
    """Mock evaluation function."""
    time.sleep(0.02)
    return _evaluation_function(*args, **kwargs)


def remove_sql_cols(df):
    df.drop(
        columns=[col for col in df.columns if col.startswith("to_run_")],
        inplace=True,
    )


@pytest.fixture
def input_df():
    return pd.DataFrame(
        {
            "name": ["test1", "test2", "test3"],
            "value": [1.0, 2.0, 3.0],
            "value_1": [2.0, 3.0, 4.0],
        }
    )


@pytest.fixture
def new_columns():
    return [["result_orig", 0.0], ["result_10", 0.0]]


@pytest.fixture
def expected_df(input_df):
    expected_result_df = input_df.copy(deep=True)
    expected_result_df.index.rename("index", inplace=True)
    expected_result_df["exception"] = None
    expected_result_df["result_orig"] = [1.0, 2.0, 3.0]
    expected_result_df["result_10"] = [20.0, 30.0, 40.0]

    return expected_result_df


class TestEvaluate:
    """Test the bluepyparallel.evaluator.evaluate function."""

    @pytest.mark.parametrize("with_sql", [True, False])
    @pytest.mark.parametrize("factory_type", [None, "multiprocessing"])
    def test_evaluate(self, input_df, new_columns, expected_df, db_url, with_sql, factory_type):
        """Test evaluator on a trivial example."""
        parallel_factory = init_parallel_factory(factory_type)

        result_df = evaluate(
            input_df,
            _evaluation_function,
            new_columns,
            parallel_factory=parallel_factory,
            db_url=db_url if with_sql else None,
        )
        if not with_sql:
            remove_sql_cols(expected_df)

        assert_frame_equal(result_df, expected_df, check_like=True)

    @pytest.mark.parametrize(
        "func_args_kwargs",
        [
            ([20.0], {}),
            ([20.0], {"coeff": 15.0}),
            ([30.0, 5.0], {}),
            ([], {"factor": 20.0, "coeff": 15.0}),
        ],
    )
    @pytest.mark.parametrize("with_sql", [True, False])
    @pytest.mark.parametrize("factory_type", [None, "multiprocessing"])
    def test_evaluate_args_kwargs(
        self,
        input_df,
        new_columns,
        expected_df,
        db_url,
        func_args_kwargs,
        with_sql,
        factory_type,
    ):
        """Test evaluator on a trivial example with passing args or kwargs."""
        parallel_factory = init_parallel_factory(factory_type)
        args, kwargs = deepcopy(func_args_kwargs)

        result_df = evaluate(
            input_df,
            _evaluation_function,
            new_columns,
            parallel_factory=parallel_factory,
            db_url=db_url if with_sql else None,
            func_args=args,
            func_kwargs=kwargs,
        )
        if not with_sql:
            remove_sql_cols(expected_df)

        # Update expected values
        for k, v in zip(["factor", "coeff"], args):
            kwargs[k] = v
        expected_df["result_10"] = kwargs.get("factor", 10) * expected_df["value_1"] + kwargs.get(
            "coeff", 0
        )

        assert_frame_equal(result_df, expected_df, check_like=True)

    @pytest.mark.parametrize("factory_type", [None, "multiprocessing"])
    def test_evaluate_resume(self, input_df, new_columns, expected_df, db_url, factory_type):
        """Test evaluator on a trivial example."""
        parallel_factory = init_parallel_factory(factory_type)

        # Compute some values
        tmp_df = evaluate(
            input_df.loc[[0, 2]],
            _evaluation_function,
            new_columns,
            parallel_factory=parallel_factory,
            db_url=db_url,
        )

        # Update the input DF
        input_df.loc[1, "value"] *= 2

        # Compute only the missing values
        result_df = evaluate(
            input_df,
            _evaluation_function,
            new_columns,
            resume=True,
            parallel_factory=parallel_factory,
            db_url=db_url,
        )

        # The values save in the DB should be the same
        assert_frame_equal(result_df.loc[[0, 2]], tmp_df, check_like=True)

        # Only the values computed after the resume should be updated
        expected_df.loc[1, "value"] *= 2
        expected_df.loc[1, "result_orig"] *= 2
        assert_frame_equal(result_df, expected_df, check_like=True)

    def test_evaluate_resume_bad_cols(self, input_df, new_columns, db_url):
        """Test evaluator on a trivial example."""
        parallel_factory = init_parallel_factory(None)

        # Compute some values
        evaluate(
            input_df.loc[[0, 2]],
            _evaluation_function,
            new_columns,
            parallel_factory=parallel_factory,
            db_url=db_url,
        )

        # Update the input DF
        input_df.loc[1, "value"] *= 2

        # Create inconsistent values in the input DF that would be overwritten if the values were
        # computed again
        input_df.loc[[0, 2], "value"] *= 999

        # Should raise a ValueError because the values changed
        with pytest.raises(
            ValueError,
            match=r"The following columns have different values from the DataBase: \['value'\]",
        ):
            evaluate(
                input_df,
                _evaluation_function,
                new_columns,
                resume=True,
                parallel_factory=parallel_factory,
                db_url=db_url,
            )

    @pytest.mark.parametrize("factory_type", [None, "multiprocessing"])
    def test_evaluate_overwrite_db(self, input_df, new_columns, expected_df, db_url, factory_type):
        """Test evaluator on a trivial example."""
        parallel_factory = init_parallel_factory(factory_type)

        # Compute once
        previous_df = input_df.copy(deep=True)
        previous_df["name"] += "_previous"
        previous_df["value"] *= 999
        previous_df["value_1"] *= 999
        tmp_df = evaluate(
            previous_df,
            _evaluation_function,
            new_columns,
            parallel_factory=parallel_factory,
            db_url=db_url,
        )
        assert (tmp_df["name"].str.endswith("_previous")).all()

        # Compute again with new values
        result_df = evaluate(
            input_df,
            _evaluation_function,
            new_columns,
            parallel_factory=parallel_factory,
            db_url=db_url,
        )
        assert_frame_equal(result_df, expected_df, check_like=True)

    class TestBenchmark:
        """Some benchmark tests."""

        @pytest.mark.parametrize("df_size", ["small", "big"])
        @pytest.mark.parametrize("function_type", ["fast", "slow"])
        @pytest.mark.parametrize("with_sql", [True, False])
        @pytest.mark.parametrize("factory_type", [None, "multiprocessing"])
        def test_evaluate(
            self,
            input_df,
            new_columns,
            expected_df,
            db_url,
            df_size,
            function_type,
            with_sql,
            factory_type,
            benchmark,
        ):
            """Test evaluator on a trivial example."""
            parallel_factory = init_parallel_factory(factory_type, processes=None)

            if df_size == "big":
                input_df = input_df.loc[np.repeat(input_df.index.values, 50)].reset_index(drop=True)
                expected_df = expected_df.loc[np.repeat(expected_df.index.values, 50)].reset_index(
                    drop=True
                )

            func = _evaluation_function if function_type == "fast" else _slow_function

            result_df = benchmark(
                evaluate,
                input_df,
                func,
                new_columns,
                parallel_factory=parallel_factory,
                db_url=db_url if with_sql else None,
            )
            if not with_sql:
                remove_sql_cols(expected_df)
            assert_frame_equal(result_df, expected_df, check_like=True)
