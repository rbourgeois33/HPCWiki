#!/bin/bash
#SBATCH -A pri@h100
#SBATCH --job-name=topo
#SBATCH -C h100
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --gres=gpu:4
#SBATCH --cpus-per-task=96
#SBATCH --hint=nomultithread
#SBATCH --time=00:05:00
#SBATCH --output=topo.out
#SBATCH --error=topo.out

module purge
module load arch/h100
module list

module load hwloc

set -x

lstopo --of svg topology.svg
nvidia-smi topo -m 
