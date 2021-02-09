from functools import partial
import pandas as pd
from pandas._testing import assert_frame_equal

from bluepyparallel import evaluate_combos
from bluepyparallel import init_parallel_factory


def _evaluation_function(combo):
    """Mock evaluation function."""
    return {"result_orig": combo["value"], "result_10": 10.0 * combo["value_1"]}


def test_evaluate_combos():
    """Test combos evaluator on a trivial example."""
    parallel_factory = init_parallel_factory("multiprocessing")
    combos = pd.DataFrame()
    combos.loc[0, "name"] = "test1"
    combos.loc[0, "value"] = 1.0
    combos.loc[0, "value_1"] = 2.0
    combos.loc[1, "name"] = "test2"
    combos.loc[1, "value"] = 2.0
    combos.loc[1, "value_1"] = 3.0

    expected_result_combos = combos.copy()
    expected_result_combos["exception"] = ""
    expected_result_combos.loc[0, "name"] = "test1"
    expected_result_combos.loc[1, "name"] = "test2"
    expected_result_combos["to_run_result_orig"] = 0
    expected_result_combos["to_run_result_10"] = 0
    expected_result_combos.loc[0, "value"] = 1.0
    expected_result_combos.loc[1, "value"] = 2.0
    expected_result_combos.loc[0, "value_1"] = 2.0
    expected_result_combos.loc[1, "value_1"] = 3.0
    expected_result_combos.loc[0, "result_orig"] = 1.0
    expected_result_combos.loc[1, "result_orig"] = 2.0
    expected_result_combos.loc[0, "result_10"] = 20.0
    expected_result_combos.loc[1, "result_10"] = 30.0

    new_columns = [["result_orig", 0.0], ["result_10", 0.0]]
    result_combos = evaluate_combos(
        combos, _evaluation_function, new_columns, parallel_factory=parallel_factory
    )
    assert_frame_equal(result_combos, expected_result_combos, check_like=True)


if __name__ == "__main__":
    test_evaluate_combos()
