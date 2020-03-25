#!/bin/bash
#SBATCH --ntasks=1
#SBATCH --qos=batch
#SBATCH --time=10:00:00
#SBATCH --mem-per-cpu=10G
#SBATCH --mail-user=hannah.blau@jax.org
#SBATCH --mail-type=END,FAIL

module load singularity

singularity pull library://fenz/prova/python:3.8.2
singularity exec python_3.8.2.sif python retrieve_pubmed_files.py
