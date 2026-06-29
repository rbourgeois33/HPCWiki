# utiliser rocprof-compute dans trust pour le hackathon

## Prérequis

- Créer un baltik à partir du trust de pierre
  - `source /lus/work/RES1/genden15/pledac/trust/next_gpu_mi300_no_mpi_rocm720/env_TRUST.sh`
  - `https://codev-tuleap.intra.cea.fr/plugins/mediawiki/wiki/trust/index.php?title=Creer_un_baltik_sur_TRUST`
  - `module load cmake/3.27.9`

- Se créer un env python pour `rocprof-compute`
  - `module load python` normalement python3.12
  - se créer un venv avec [ces requirements](https://github.com/rbourgeois33/rocprof_tests/blob/main/requirements.txt)
  - tester que `rocprof-compute` renvoie bien un message 
  
- prendre un cas test trust:
  - cd baltik
  - trust -copy JEL_bous (sourcer trust pas le baltik la)
  - mettre `solveur_pression gcp { precond ssor { omega 1.6 } seuil 1e30 }` en solveur pression
  - tester $exec JEL_bous
  
- profiler
  - `rocprof-compute profile --name "base" -- $exec JEL_bous`
  - `rocprof-compute analyze -p workloads/bench/MI300A_A1/`
  - Ca sort un `pmc_dispatch_info.csv`, tu reperes l'ID puis
  - `rocprof-compute analyze -p workloads/bench/MI300A_A1/ --dispatch 363 -b 2`
  - varier b pour voir dautres infos



- Profiler finement les lignes des kernels: (voir slides etienne)

Installer le .so dans $WORK

`rocprofv3 --att --att-library-path=$WORK --kernel-rename --kokkos-trace  --output-directory rocprofv3-fine-base --kernel-include-regex "(compute_flux_tetra_kernel|ajouter_elem)"  --kernel-iteration-range "[1-10]" -- $exec GPU4_BENCH_HACKATHON`

-> loader dans `rocprof-compute-viewer` (PAS LE MEME que `rocprof-compute --gui` !!)

- Profiler application: (trust -rocprof)
  
`rocprofv3 -o GPU4_BENCH_HACKATHON --output-format=pftrace --stats --memory-allocation-trace --runtime-trace --hip-trace --kernel-trace --scratch-memory-trace --kokkos-trace -- $exec GPU4_BENCH_HACKATHON -use_gpu_aware_mpi 0`

-> loader dans perfetto

Cool:
- Les .csv ca s'ouve dans excel


clean spack install:

 - spack gc

vef dis Lire dis { reorder { algo none } }

TODO:
-Spiller que 4 doubles

