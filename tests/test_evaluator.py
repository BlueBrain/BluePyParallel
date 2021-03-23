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


def _failing_function(row, factor=10.0, coeff=0.0):
    """Mock evaluation function."""
    if row["value"] == 1:
        raise ValueError("The value should not be 1")
    return {"result_orig": row["value"], "result_10": factor * row["value_1"] + coeff}


def _interrupting_function(row, *args, **kwargs):
    """Mock evaluation function."""
    if row["value"] == 2:
        raise KeyboardInterrupt
    return _evaluation_function(row, *args, **kwargs)


def _slow_function(row, *args, sleep_time=0.02, **kwargs):
    """Mock evaluation function."""
    if "sleep_time" in row:
        sleep_time = row["sleep_time"]
    time.sleep(sleep_time)
    return _evaluation_function(row, *args, **kwargs)


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
    def test_evaluate(self, input_df, new_columns, expected_df, db_url, with_sql, parallel_factory):
        """Test evaluator on a trivial example."""
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

    def test_evaluate_no_factory(self, input_df, new_columns, expected_df):
        """Test evaluator with no given factory."""
        result_df = evaluate(
            input_df,
            _evaluation_function,
            new_columns,
        )
        remove_sql_cols(expected_df)

        assert_frame_equal(result_df, expected_df, check_like=True)

    def test_evaluate_drop_exception_col(self, input_df, new_columns, expected_df):
        """Test evaluator with exception column in input DF."""
        input_df["exception"] = 1
        result_df = evaluate(
            input_df,
            _evaluation_function,
            new_columns,
        )
        remove_sql_cols(expected_df)

        assert_frame_equal(result_df, expected_df, check_like=True)

    def test_evaluate_no_new_columns(self, input_df, expected_df):
        """Test evaluator with no new columns given."""
        result_df = evaluate(
            input_df,
            _evaluation_function,
        )
        remove_sql_cols(expected_df)

        assert_frame_equal(result_df, expected_df, check_like=True)

    def test_evaluate_empty_df(self, input_df, expected_df):
        """Test evaluator on an empty DF."""
        result_df = evaluate(
            input_df.loc[[]],
            _evaluation_function,
        )
        remove_sql_cols(expected_df)

        assert result_df.empty
        assert result_df.columns.tolist() == ["name", "value", "value_1", "exception"]

    def test_evaluate_exception(self, input_df, expected_df):
        """Test evaluator with a function that raises an exception."""
        result_df = evaluate(
            input_df,
            _failing_function,
        )
        remove_sql_cols(expected_df)

        assert_frame_equal(result_df.loc[[1, 2]], expected_df.loc[[1, 2]], check_like=True)
        equal_cols = ["name", "value", "value_1"]
        not_equal_cols = ["exception", "result_orig", "result_10"]
        assert_frame_equal(
            result_df.loc[[0], equal_cols], expected_df.loc[[0], equal_cols], check_like=True
        )
        assert (
            (result_df.loc[[0], not_equal_cols] != expected_df.loc[[0], not_equal_cols]).all().all()
        )
        assert "The value should not be 1" in result_df.loc[0, "exception"]

    def test_evaluate_keyboard_interrupt(self, input_df, expected_df):
        """Test evaluator with a KeyboardInterrupt: only the first element shold be computed."""
        result_df = evaluate(
            input_df,
            _interrupting_function,
        )
        remove_sql_cols(expected_df)

        expected_df.loc[[1, 2], ["result_orig", "result_10"]] = None

        assert_frame_equal(result_df, expected_df, check_like=True)

    @pytest.fixture
    def func_args_kwargs(self):
        return [
            ([], {}),
            ([10.0], {}),
            ([], {"coeff": 5.0}),
            ([20.0, 15.0], {}),
            ([30.0], {"coeff": 25.0}),
            ([], {"factor": 40.0, "coeff": 35.0}),
        ]

    @pytest.mark.parametrize("with_sql", [True, False])
    def test_evaluate_args_kwargs(
        self,
        input_df,
        new_columns,
        expected_df,
        db_url,
        func_args_kwargs,
        with_sql,
        parallel_factory,
    ):
        """Test evaluator on a trivial example with passing args or kwargs."""
        for i in func_args_kwargs:
            args, kwargs = deepcopy(i)
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
            expected_df["result_10"] = kwargs.get("factor", 10) * expected_df[
                "value_1"
            ] + kwargs.get("coeff", 0)

            assert_frame_equal(result_df, expected_df, check_like=True)

    def test_evaluate_resume(self, input_df, new_columns, expected_df, db_url, parallel_factory):
        """Test evaluator on a trivial example."""
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

    def test_evaluate_overwrite_db(
        self, input_df, new_columns, expected_df, db_url, parallel_factory
    ):
        """Test evaluator on a trivial example."""
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
    def test_evaluate(
        self,
        input_df,
        new_columns,
        expected_df,
        db_url,
        df_size,
        function_type,
        with_sql,
        parallel_factory,
        benchmark,
    ):
        """Test evaluator on a trivial example."""
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
