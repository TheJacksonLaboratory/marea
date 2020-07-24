#!/bin/bash
#SBATCH --ntasks=1
#SBATCH --qos=batch
#SBATCH --time=23:00:00
#SBATCH --mem-per-cpu=50G
#SBATCH --mail-user=hannah.blau@jax.org
#SBATCH --mail-type=END,FAIL

module load singularity

singularity exec marea_python.sif python ../scripts/replace_concepts.py -p /projects/robinson-lab/marea/data \
-r /projects/robinson-lab/marea/data/pubmed_rel -o /projects/robinson-lab/marea/data/pubmed_cr
