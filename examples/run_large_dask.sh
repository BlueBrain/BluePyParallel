#!/bin/bash -l
#SBATCH --nodes=1             # Number of nodes
#SBATCH --time=00:10:00       # Time limit
#SBATCH --partition=prod
#SBATCH --constraint=cpu
#SBATCH --mem=0
#SBATCH --cpus-per-task=1
#SBATCH --account=proj82      # your project number
#SBATCH --job-name=test_bpp
set -e


module purge
module load unstable py-mpi4py
module load unstable py-dask-mpi
module load unstable py-bglibpy
module load unstable neurodamus-neocortex

deactivate
. venv/bin/activate

unset PMI_RANK

srun python large_computation.py dask
