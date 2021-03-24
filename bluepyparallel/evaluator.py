"""Module to evaluate generic functions on rows of dataframe."""
import logging
import sys
import traceback
from functools import partial

import pandas as pd
from tqdm import tqdm

from bluepyparallel.database import DataBase
from bluepyparallel.parallel import init_parallel_factory

logger = logging.getLogger(__name__)


def _try_evaluation(task, evaluation_function, func_args, func_kwargs):
    """Encapsulate the evaluation function into a try/except and isolate to record exceptions."""
    task_id, task_args = task
    try:
        result = evaluation_function(task_args, *func_args, **func_kwargs)
        exception = None
    except Exception:  # pylint: disable=broad-except
        result = {}
        exception = "".join(traceback.format_exception(*sys.exc_info()))
        logger.exception("Exception for ID=%s: %s", task_id, exception)
    return task_id, result, exception


def evaluate(
    df,
    evaluation_function,
    new_columns=None,
    resume=False,
    parallel_factory=None,
    db_url=None,
    func_args=None,
    func_kwargs=None,
    **mapper_kwargs,
):
    """Evaluate and save results in a sqlite database on the fly and return dataframe.

    Args:
        df (pandas.DataFrame): each row contains information for the computation.
        evaluation_function (callable): function used to evaluate each row,
            should have a single argument as list-like containing values of the rows of df,
            and return a dict with keys corresponding to the names in new_columns.
        new_columns (list): list of names of new column and empty value to save evaluation results,
            i.e.: :code:`[['result', 0.0], ['valid', False]]`.
        resume (bool): if :obj:`True` and ``db_url`` is provided, it will use only compute the
            missing rows of the database.
        parallel_factory (ParallelFactory or str): parallel factory name or instance.
        db_url (str): should be DB URL that can be interpreted by :func:`sqlalchemy.create_engine`
            or can be a file path that is interpreted as a SQLite database. If an URL is given,
            the SQL backend will be enabled to store results and allowing future resume. Should
            not be used when evaluations are numerous and fast, in order to avoid the overhead of
            communication with the SQL database.
        func_args (list): the arguments to pass to the evaluation_function.
        func_kwargs (dict): the keyword arguments to pass to the evaluation_function.
        **mapper_kwargs: the keyword arguments are passed to the get_mapper() method of the
            :class:`ParallelFactory` instance.

    Return:
        pandas.DataFrame: dataframe with new columns containing the computed results.
    """
    # Initialize the parallel factory
    if isinstance(parallel_factory, str) or parallel_factory is None:
        parallel_factory = init_parallel_factory(parallel_factory)
    # Set default args
    if func_args is None:
        func_args = []

    # Set default kwargs
    if func_kwargs is None:
        func_kwargs = {}

    # Drop exception column if present
    if "exception" in df.columns:
        logger.warning("The 'exception' column is going to be replaced")
        df = df.drop(columns=["exception"])

    # Shallow copy the given DataFrame to add internal rows
    to_evaluate = df.copy()
    task_ids = to_evaluate.index

    # Set default new columns
    if new_columns is None:
        new_columns = []

    # Setup internal and new columns
    to_evaluate["exception"] = None
    for new_column in new_columns:
        to_evaluate[new_column[0]] = new_column[1]

    # Create the database if required and get the task ids to run
    if db_url is None:
        logger.info("Not using SQL backend to save iterations")
        db = None
    else:
        db = DataBase(db_url)

        if resume and db.exists("df"):
            logger.info("Load data from SQL database")
            db.reflect("df")
            previous_results = db.load()
            previous_idx = previous_results.index
            bad_cols = [
                col
                for col in df.columns
                if not to_evaluate.loc[previous_idx, col].equals(previous_results[col])
            ]
            if bad_cols:
                raise ValueError(
                    f"The following columns have different values from the DataBase: {bad_cols}"
                )
            to_evaluate.loc[previous_results.index] = previous_results.loc[previous_results.index]
            task_ids = task_ids.difference(previous_results.index)
        else:
            logger.info("Create SQL database")
            db.create(to_evaluate)

        db_url = db.get_url()

    # Log the number of tasks to run
    if len(task_ids) > 0:
        logger.info("%s rows to compute.", str(len(task_ids)))
    else:
        logger.warning("WARNING: No row to compute, something may be wrong")
        return to_evaluate

    # Get the factory mapper
    mapper = parallel_factory.get_mapper(**mapper_kwargs)

    # Setup the function to apply to the data
    eval_func = partial(
        _try_evaluation,
        evaluation_function=evaluation_function,
        func_args=func_args,
        func_kwargs=func_kwargs,
    )

    # Split the data into rows
    arg_list = list(to_evaluate.loc[task_ids, df.columns].to_dict("index").items())

    res = []
    try:
        # Compute and collect the results
        for task_id, result, exception in tqdm(mapper(eval_func, arg_list), total=len(task_ids)):
            res.append(dict({"df_index": task_id, "exception": exception}, **result))

            # Save the results into the DB
            if db is not None:
                db.write(
                    task_id, result, exception, **to_evaluate.loc[task_id, df.columns].to_dict()
                )

    except (KeyboardInterrupt, SystemExit) as ex:
        # To save dataframe even if program is killed
        logger.warning("Stopping mapper loop. Reason: %r", ex)

    # Gather the results to the output DataFrame
    res_df = pd.DataFrame(res)
    res_df.set_index("df_index", inplace=True)
    to_evaluate.loc[res_df.index, res_df.columns] = res_df

    return to_evaluate
