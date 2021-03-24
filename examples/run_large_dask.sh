#!/bin/bash -l

# SBATCH --nodes=1             # Number of nodes
# SBATCH --time=00:10:00       # Time limit
# SBATCH --partition=prod
# SBATCH --constraint=cpu
# SBATCH --mem=0
# SBATCH --cpus-per-task=1
# SBATCH --account=proj82      # your project number
# SBATCH --job-name=test_bpp

# # Dask configuration
# export DASK_DISTRIBUTED__LOGGING__DISTRIBUTED="info"
# export DASK_DISTRIBUTED__WORKER__USE_FILE_LOCKING=False
# export DASK_DISTRIBUTED__WORKER__MEMORY__TARGET=False  # don't spill to disk
# export DASK_DISTRIBUTED__WORKER__MEMORY__SPILL=False  # don't spill to disk
# export DASK_DISTRIBUTED__WORKER__MEMORY__PAUSE=0.80  # pause execution at 80% memory use
# export DASK_DISTRIBUTED__WORKER__MEMORY__TERMINATE=0.95  # restart the worker at 95% use
# export DASK_DISTRIBUTED__WORKER__MULTIPROCESSING_METHOD=spawn
# export DASK_DISTRIBUTED__WORKER__DAEMON=True
# # Reduce dask profile memory usage/leak (see https://github.com/dask/distributed/issues/4091)
# export DASK_DISTRIBUTED__WORKER__PROFILE__INTERVAL=10000ms  # Time between statistical profiling queries
# export DASK_DISTRIBUTED__WORKER__PROFILE__CYCLE=1000000ms  # Time between starting new profile

# # Split tasks to avoid some dask errors (e.g. Event loop was unresponsive in Worker)
# export PARALLEL_BATCH_SIZE=1000

set -e


module purge
module load unstable py-mpi4py
module load unstable py-dask-mpi
module load unstable py-bglibpy
module load unstable neurodamus-neocortex

. ~/base/bin/activate

unset PMI_RANK

srun python large_computation.py dask 100000 1000
