#!/bin/bash -l
#SBATCH --nodes=1            # Number of nodes
#SBATCH --time=24:00:00       # Time limit
#SBATCH --partition=prod      # Submit to the production 'partition'
#SBATCH --constraint=cpu      # Constraint the job to run on nodes with/without SSDs. If you want SSD, use only "nvme". If you want KNLs then "knl"
#SBATCH --mem=0
#SBATCH --cpus-per-task=1
#SBATCH --account=proj82      # your project number
#SBATCH --job-name=test_bpp
set -e

export OPENBLAS_NUM_THREADS=1
export OMP_NUM_THREADS=1

export IPYTHONDIR=${PWD}/.ipython
export IPYTHON_PROFILE=benchmark.${SLURM_JOBID}
ipcontroller --init --ip='*' --sqlitedb --ping=30000 --profile=${IPYTHON_PROFILE} &
sleep 10
srun --output="${LOGS}/engine_%j_%2t.out" ipengine --timeout=300 --profile=${IPYTHON_PROFILE} &
sleep 10

python large_computation.py ipyparallel
