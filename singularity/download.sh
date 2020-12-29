#!/bin/bash
#SBATCH --ntasks=1
#SBATCH --qos=batch
#SBATCH --time=23:00:00
#SBATCH --mem-per-cpu=2G
#SBATCH --mail-user=hannah.blau@jax.org
#SBATCH --mail-type=END,FAIL

module load singularity

singularity exec marea_python.sif python ../scripts/retrieve_pubmed_files.py \
 -x /projects/robinson-lab/marea/data/pubmed_xml/
