#!/bin/bash

#SBATCH --job-name=pasqal_local_job
#SBATCH --output=/home/slurmuser/data/hello_%j.out
#SBATCH --error=/home/slurmuser/data/hello_%j.out
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1

# Your script goes here
echo Hello, World!