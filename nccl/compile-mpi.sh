#!/bin/bash
#SBATCH -A pri@h100
#SBATCH --job-name=compile-mpi
#SBATCH -C h100                      # partition gpu_p6 : noeud quadri-GPU H100 80 Go
#SBATCH --nodes=1                    # nombre de noeuds
#SBATCH --ntasks-per-node=1          # nombre de taches par noeud (= nombre de GPU par noeud ici)
#SBATCH --gres=gpu:0                 # nombre de GPU par noeud (max 4)
#SBATCH --cpus-per-task=24           # nombre de CPU par tache pour gpu_p6 (1/4 des CPU du noeud 4-GPU H100)
#SBATCH --hint=nomultithread         # hyperthreading desactive
#SBATCH --time=00:30:00              # temps maximum d'execution demande (HH:MM:SS)
#SBATCH --output=compile-mpi%j.out     # nom du fichier de sortie (%j est remplacé par le numéro du travail)
#SBATCH --error=compile-mpi%j.out      # nom du fichier d'erreur (ici commun avec la sortie)

# Nettoyage des modules charges en interactif et herites par defaut
module purge

# Activation du module permet l'accès aux modules compatibles avec la partition H100
module load arch/h100

# Chargement des modules
module load gcc/14.2.0 nccl/2.28.9-1-cuda openmpi/4.1.8
module list 

echo $CUDA_HOME
which nvcc
echo $OPENMPI_ROOT
which mpicc
echo $NCCL_ROOT
echo $CXX
which gcc

# Echo des commandes lancees
set -x

# Execution du code
make MPI=1 CUDA_HOME=$CUDA_HOME MPI_HOME=$OPENMPI_ROOT NCCL_HOME=$NCCL_ROOT NAME_SUFFIX=_mpi -j 24
