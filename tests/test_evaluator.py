"""Test the bluepyparallel.evaluator module"""
import sqlite3

import pandas as pd
import pytest
from pandas._testing import assert_frame_equal

from bluepyparallel import evaluate
from bluepyparallel import init_parallel_factory


def _evaluation_function(combo):
    """Mock evaluation function."""
    return {"result_orig": combo["value"], "result_10": 10.0 * combo["value_1"]}


def reset_sql_row(db_filename, row_id, new_columns):
    with sqlite3.connect(str(db_filename)) as db:
        vals = ", ".join([f"to_run_{i}=1, {i}=-1" for i in new_columns])
        db.execute("UPDATE df SET " + vals + " WHERE `index`=" + str(row_id))


def remove_sql_cols(df):
    df.drop(
        columns=[col for col in df.columns if col.startswith("to_run_") or col == "exception"],
        inplace=True,
    )


class TestEvaluate:
    """Test the bluepyparallel.evaluator.evaluate function."""

    @pytest.fixture
    def input_df(self):
        return pd.DataFrame(
            {
                "name": ["test1", "test2", "test3"],
                "value": [1.0, 2.0, 3.0],
                "value_1": [2.0, 3.0, 4.0],
            }
        )

    @pytest.fixture
    def new_columns(self):
        return [["result_orig", 0.0], ["result_10", 0.0]]

    @pytest.fixture
    def expected_df(self, input_df):
        expected_result_df = input_df.copy(deep=True)
        expected_result_df["exception"] = ""
        expected_result_df["to_run_result_orig"] = 0
        expected_result_df["to_run_result_10"] = 0
        expected_result_df["result_orig"] = [1.0, 2.0, 3.0]
        expected_result_df["result_10"] = [20.0, 30.0, 40.0]

        return expected_result_df

    @pytest.mark.parametrize("with_sql", [True, False])
    @pytest.mark.parametrize("factory_type", [None, "multiprocessing"])
    def test_evaluate(
        self, input_df, new_columns, expected_df, db_filename, with_sql, factory_type
    ):
        """Test evaluator on a trivial example."""
        parallel_factory = init_parallel_factory(factory_type)

        result_df = evaluate(
            input_df,
            _evaluation_function,
            new_columns,
            parallel_factory=parallel_factory,
            db_filename=db_filename if with_sql else None,
        )
        if not with_sql:
            remove_sql_cols(expected_df)
        assert_frame_equal(result_df, expected_df, check_like=True)

    @pytest.mark.parametrize("factory_type", [None, "multiprocessing"])
    def test_evaluate_resume(self, input_df, new_columns, expected_df, db_filename, factory_type):
        """Test evaluator on a trivial example."""
        parallel_factory = init_parallel_factory(factory_type)

        # Compute all values
        tmp_df = evaluate(
            input_df,
            _evaluation_function,
            new_columns,
            parallel_factory=parallel_factory,
            db_filename=db_filename,
        )

        # Reset DB for one row
        reseted_cols = [
            "result_orig",
            "result_10",
        ]
        reset_sql_row(
            db_filename,
            0,
            reseted_cols,
        )

        # Compute only the missing values
        result_df = evaluate(
            input_df,
            _evaluation_function,
            new_columns,
            resume=True,
            parallel_factory=parallel_factory,
            db_filename=db_filename,
        )
        assert_frame_equal(result_df, tmp_df, check_like=True)
        assert_frame_equal(result_df, expected_df, check_like=True)

    @pytest.mark.parametrize("factory_type", [None, "multiprocessing"])
    def test_evaluate_overwrite_db(
        self, input_df, new_columns, expected_df, db_filename, factory_type
    ):
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
            db_filename=db_filename,
        )
        assert (tmp_df["name"].str.endswith("_previous")).all()

        # Compute again with new values
        result_df = evaluate(
            input_df,
            _evaluation_function,
            new_columns,
            parallel_factory=parallel_factory,
            db_filename=db_filename,
        )
        assert_frame_equal(result_df, expected_df, check_like=True)
