"""Module to evaluate generic functions on rows of dataframe."""
import logging
import sqlite3
import sys
import traceback
from collections import defaultdict
from functools import partial
from pathlib import Path

import pandas as pd
from tqdm import tqdm

from bluepyparallel.parallel import init_parallel_factory

logger = logging.getLogger(__name__)


def _try_evaluation(task, evaluation_function=None):
    """Encapsulate the evaluation function into a try/except and isolate to record exceptions."""
    task_id, task_args = task
    try:
        result = evaluation_function(task_args)
        exception = ""
    except Exception:  # pylint: disable=broad-except
        result = None
        exception = "".join(traceback.format_exception(*sys.exc_info()))
        logger.exception("Exception for ID=%s: %s", task_id, exception)
    return task_id, result, exception


def _create_database(df, new_columns, db_filename="db.sql"):
    """Create a sqlite database from dataframe."""
    df["exception"] = None
    for new_column in new_columns:
        df[new_column[0]] = new_column[1]
        df["to_run_" + new_column[0]] = 1
    with sqlite3.connect(str(db_filename)) as db:
        df.to_sql("df", db, if_exists="replace", index_label="index")
    return df


def _load_database_to_dataframe(db_filename="db.sql"):
    """Load an SQL database and construct the dataframe."""
    with sqlite3.connect(str(db_filename)) as db:
        out = pd.read_sql("SELECT * FROM df", db, index_col="index")
        return out


def _write_to_sql(db_filename, task_id, results, new_columns, exception):
    """Write row data to SQL."""
    with sqlite3.connect(str(db_filename)) as db:
        for new_column in new_columns:
            res = results[new_column[0]] if results is not None else None
            db.execute(
                "UPDATE df SET " + new_column[0] + "=?, "
                "exception=?, to_run_" + new_column[0] + "=? WHERE `index`=?",
                (res, exception, 0, task_id),
            )


def evaluate(
    df,
    evaluation_function,
    new_columns=None,
    resume=False,
    parallel_factory=None,
    db_filename=None,
):
    """Evaluate and save results in a sqlite database on the fly and return dataframe.

    Args:
        df (DataFrame): each row contains information for the computation
        evaluation_function (function): function used to evaluate each row,
            should have a single argument as list-like containing values of the rows of df,
            and return a dict with keys corresponding to the names in new_columns
        new_columns (list): list of names of new column and empty value to save evaluation results,
            i.e.: [['result', 0.0], ['valid', False]]
        resume (bool): if True, it will use only compute the empty rows of the database,
            if False, it will ecrase or generate the database
        parallel_factory (ParallelFactory): parallel factory instance
        db_filename (str): if a file path is given, SQL backend will be enabled and will use this
            path for the SQLite database. Should not be used when evaluations are numerous and
            fast, in order to avoid the overhead of communication with SQL database.

    Return:
        pandas.DataFrame: dataframe with new columns containing computed results
    """
    if isinstance(parallel_factory, str) or parallel_factory is None:
        parallel_factory = init_parallel_factory(parallel_factory)

    task_ids = df.index

    if new_columns is None:
        new_columns = [["data", ""]]

    if db_filename is None:
        logger.info("Not using SQL backend to save iterations")
        to_evaluate = df
    elif resume:
        logger.info("Load data from SQL database")
        if Path(db_filename).exists():
            to_evaluate = _load_database_to_dataframe(db_filename=db_filename)
            task_ids = task_ids.intersection(to_evaluate.index)
        else:
            to_evaluate = _create_database(df, new_columns, db_filename=db_filename)

        # Find tasks to run
        should_run = (
            to_evaluate.loc[task_ids, ["to_run_" + col[0] for col in new_columns]] == 1
        ).any(axis=1)
        task_ids = should_run.loc[should_run].index
    else:
        logger.info("Create SQL database")
        to_evaluate = _create_database(df, new_columns, db_filename=db_filename)

    if len(task_ids) > 0:
        logger.info("%s rows to compute.", str(len(task_ids)))
    else:
        logger.warning("WARNING: No row to compute, something may be wrong")
        return _load_database_to_dataframe(db_filename)

    mapper = parallel_factory.get_mapper()

    eval_func = partial(_try_evaluation, evaluation_function=evaluation_function)
    arg_list = to_evaluate.to_dict("index").items()

    if db_filename is None:
        _results = defaultdict(dict)

    try:
        for task_id, results, exception in tqdm(mapper(eval_func, arg_list), total=len(task_ids)):
            if db_filename is None:
                for new_column, _ in new_columns:
                    _results[new_column][task_id] = (
                        results[new_column] if results is not None else None
                    )
            else:
                _write_to_sql(
                    db_filename,
                    task_id,
                    results,
                    new_columns,
                    exception,
                )
    except (KeyboardInterrupt, SystemExit) as ex:
        # To save dataframe even if program is killed
        logger.warning("Stopping mapper loop. Reason: %r", ex)

    if db_filename is None:
        to_evaluate = pd.concat([to_evaluate, pd.DataFrame(_results)], axis=1)
        return to_evaluate
    return _load_database_to_dataframe(db_filename)
