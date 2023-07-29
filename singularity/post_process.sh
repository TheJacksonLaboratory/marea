#!/bin/bash
#SBATCH --ntasks=1
#SBATCH --qos=batch
#SBATCH --time=23:00:00
#SBATCH --mem-per-cpu=5G
#SBATCH --mail-user=hannah.blau@jax.org
#SBATCH --mail-type=END,FAIL

module load singularity

singularity exec marea_python.sif python ../scripts/post_process.py \
-p /projects/robinson-lab/marea/pubtator/current -r /projects/robinson-lab/marea/data/pubmed_rel \
-n /projects/robinson-lab/marea/data/nltk_data -o /projects/robinson-lab/marea/data/pubmed_cr/new
