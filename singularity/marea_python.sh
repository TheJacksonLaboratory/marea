#!/bin/bash
#SBATCH --ntasks=1
#SBATCH --qos=batch
#SBATCH --time=1:00:00
#SBATCH --mem-per-cpu=5G
#SBATCH --mail-user=hannah.blau@jax.org
#SBATCH --mail-type=END,FAIL

module load singularity

singularity run http://s3-far.jax.org/builder/builder marea_python.def marea_python.sif
