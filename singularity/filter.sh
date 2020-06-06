#!/bin/bash
#SBATCH --ntasks=1
#SBATCH --qos=batch
#SBATCH --time=23:00:00
#SBATCH --mem-per-cpu=30G
#SBATCH --mail-user=hannah.blau@jax.org
#SBATCH --mail-type=END,FAIL

module load singularity

singularity exec marea_python.sif python ../scripts/xml2txt.py -x /projects/robinson-lab/marea/data/pubmed_xml \
 -t /projects/robinson-lab/marea/data/pubmed_txt
singularity exec marea_python.sif python ../scripts/filter_abstracts.py -i /projects/robinson-lab/marea/data/pubmed_txt \
 -o /projects/robinson-lab/marea/data/pubmed_rel D009369 D011494
