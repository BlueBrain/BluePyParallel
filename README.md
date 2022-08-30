# BluePyParallel: Bluebrain Python Embarassingly Parallel library

Provides an embarassingly parallel tool with sql backend.

## Introduction

Provides an embarassingly parallel tool with sql backend, inspired by [BluePyMM](https://github.com/BlueBrain/BluePyMM).


## Installation

This package should be installed using pip:

```bash
pip install bluepyparallel
```


## Usage

### General computation

```python

factory_name = "multiprocessing"  # Can also be None, dask or ipyparallel
batch_size = 10  # This value is used to split the data into batches before processing them
chunk_size = 1000  # This value is used to gather the elements to process before sending them to the workers

# Setup the parallel factory
parallel_factory = init_parallel_factory(
    factory_name,
    batch_size=batch_size,
    chunk_size=chunk_size,
    processes=4,  # This parameter is specific to the multiprocessing factory
)

# Get the mapper from the factory
mapper = parallel_factory.get_mapper()

# Use the mapper to map the given function to each element of mapped_data and gather the results
result = sorted(mapper(function, mapped_data, *function_args, **function_kwargs))
```


### Working with Pandas and SQL backend

This library provides a specific function working with large :class:`pandas.DataFrame`: :func:`bluepyparallel.evaluator.evaluate`.
This function converts the DataFrame into a list of dict (one for each row), then maps a given function to element and finally gathers the results.
As it aims at working with time consuming functions, it also provides a checkpoint and resume mechanism using a SQL backend.
The SQL backend uses the [SQLAlchemy](https://docs.sqlalchemy.org) library, so it can work with a large variety of database types (like SQLite, PostgreSQL, MySQL, ...).
To activate this feature, just pass a [URL that can be processed by SQLAlchemy](https://docs.sqlalchemy.org/en/latest/core/engines.html?highlight=url#database-urls)  to the ``db_url`` parameter of :func:`bluepyparallel.evaluator.evaluate`.

.. note:: A specific driver might have to be installed to access the database (like `psycopg2 <https://www.psycopg.org/docs/>`_ for PostgreSQL for example).

Example:

```python
# Use the mapper to map the given function to each element of the DataFrame
result_df = evaluate(
    input_df,  # This is the DataFrame to process
    evaluation_function,  # This is the function that should be applied to each row of the DataFrame
    parallel_factory="multiprocessing",  # This could also be a Factory previously defined
    db_url="sqlite:///db.sql",  # This could also just be "db.sql" and would be automatically turned to SQLite URL
)
```

Now, if the computation crashed for any reason, the partial result is stored in the ``db.sql`` file.
If the crash was due to an external cause (therefore executing the code again should work), it is possible to resume the
computation from the last computed element. Thus, only the missing elements are computed, which can save a lot of time.


## Running using Dask

This is an example of a [sbatch](https://slurm.schedmd.com/sbatch.html) script that can be adapted to execute the script using multiple nodes and workers.
In this example, the code called by the ``<command>`` should parallelized using BluePyParallel.

Dask variables are not strictly required, but highly recommended, and they can be fine tuned.


```bash
#!/bin/bash -l

# Dask configuration
export DASK_DISTRIBUTED__LOGGING__DISTRIBUTED="info"
export DASK_DISTRIBUTED__WORKER__USE_FILE_LOCKING=False
export DASK_DISTRIBUTED__WORKER__MEMORY__TARGET=False  # don't spill to disk
export DASK_DISTRIBUTED__WORKER__MEMORY__SPILL=False  # don't spill to disk
export DASK_DISTRIBUTED__WORKER__MEMORY__PAUSE=0.80  # pause execution at 80% memory use
export DASK_DISTRIBUTED__WORKER__MEMORY__TERMINATE=0.95  # restart the worker at 95% use
export DASK_DISTRIBUTED__WORKER__MULTIPROCESSING_METHOD=spawn
export DASK_DISTRIBUTED__WORKER__DAEMON=True
# Reduce dask profile memory usage/leak (see https://github.com/dask/distributed/issues/4091)
export DASK_DISTRIBUTED__WORKER__PROFILE__INTERVAL=10000ms  # Time between statistical profiling queries
export DASK_DISTRIBUTED__WORKER__PROFILE__CYCLE=1000000ms  # Time between starting new profile

# Split tasks to avoid some dask errors (e.g. Event loop was unresponsive in Worker)
export PARALLEL_BATCH_SIZE=1000

srun -v <command>
```
