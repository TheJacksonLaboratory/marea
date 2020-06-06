#!/bin/bash
#SBATCH --ntasks=1
#SBATCH --qos=batch
#SBATCH --time=10:00:00
#SBATCH --mem-per-cpu=10G
#SBATCH --mail-user=hannah.blau@jax.org
#SBATCH --mail-type=END,FAIL

module load singularity

singularity run http://s3-far.jax.org/builder/builder marea_python.def marea_python.sif
singularity exec marea_python.sif python ../scripts/retrieve_pubmed_names.py -d /projects/robinson-lab/marea/data/
singularity exec marea_python.sif python ../scripts/retrieve_pubmed_files.py -d /projects/robinson-lab/marea/data/ \
 -x /projects/robinson-lab/marea/data/pubmed_xml/
