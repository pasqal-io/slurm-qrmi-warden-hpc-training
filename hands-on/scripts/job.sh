#!/bin/bash

#SBATCH --job-name=pasqal_local_job
#SBATCH --output=/home/slurmuser/data/job_%j.out
#SBATCH --error=/home/slurmuser/data/job_%j.out
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --qpu=PASQAL_LOCAL
#SBATCH --nodelist=c1

# Your script goes here
source $HOME/venv/bin/activate
python $HOME/scripts/test_env.py
# python $HOME/scripts/test_pulser_qrmi.py
# python $HOME/scripts/test_qoolqit_qrmi.py
# python $HOME/scripts/test_qubo_qrmi.py
