#!/usr/bin/env python3
"""
SLURM Job Generator & Submitter for NCCL benchmark tests on Jean Zay H100.

Writes a script named <test>-N<nodes>.sh and submits it via sbatch.
All NCCL benchmark flags are passed through verbatim to the binary.

Usage:
    python nccl_job_generator.py --nodes 2 -b 8 -e 8G -f 2 -n 20
    python nccl_job_generator.py --sweep-nodes 1 2 4 8 -b 8 -e 8G -f 2
"""

import argparse
import os
import subprocess
import sys

DEFAULT_ACCOUNT   = "pri@h100"
DEFAULT_TIME      = "00:04:59"
DEFAULT_BUILD_DIR = "./build"
DEFAULT_TEST      = "all_reduce_perf_mpi"

def render_script(nodes, test, account, time_limit, build_dir, nccl_args):
    short    = test.replace("_perf_mpi", "").replace("_", "-")
    job_name = f"{short}-N{nodes}"
    out_file = f"{job_name}.out"

    lines = [
        "#!/bin/bash",
        f"#SBATCH -A {account}",
        f"#SBATCH --job-name={job_name}",
        "#SBATCH -C h100",
        f"#SBATCH --nodes={nodes}",
        "#SBATCH --ntasks-per-node=4",
        "#SBATCH --gres=gpu:4",
        "#SBATCH --exclusive",
        "#SBATCH --cpus-per-task=24",
        "#SBATCH --hint=nomultithread",
        f"#SBATCH --time={time_limit}",
        f"#SBATCH --output={out_file}",
        f"#SBATCH --error={out_file}",
        "",
        "module purge",
        "module load arch/h100",
        "",
        "module load gcc/14.2.0 nccl/2.28.9-1-cuda openmpi/4.1.8",
        "module list",
        "",
        "export NCCL_DEBUG=INFO",
        "export NCCL_TOPO_DUMP_FILE=ncclSystem.txt",
        "",
        "set -x",
        f"srun --ntasks={nodes * 4} --nodes={nodes} {build_dir}/{test} {nccl_args}",
    ]
    return job_name, "\n".join(lines) + "\n"


def write_and_submit(job_name, script):
    script_file = f"{job_name}.sh"
    with open(script_file, "w") as f:
        f.write(script)
    os.chmod(script_file, 0o755)
    print(f"[WRITTEN]   {script_file}")

    result = subprocess.run(["sbatch", script_file], capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(
            f"sbatch failed (rc={result.returncode}):\n"
            f"  stdout: {result.stdout.strip()}\n"
            f"  stderr: {result.stderr.strip()}"
        )
    return result.stdout.strip().split()[-1]


def main():
    p = argparse.ArgumentParser(
        description="Generate and submit SLURM jobs for NCCL benchmarks on Jean Zay H100.",
        epilog=__doc__,
    )
    p.add_argument("--nodes", "-N", type=int, default=None,
                   help="Number of nodes (required unless --sweep-nodes is used)")
    p.add_argument("--sweep-nodes", nargs="+", type=int, metavar="N",
                   help="Submit one job per node count, e.g. --sweep-nodes 1 2 4 8")
    p.add_argument("--test",      default=DEFAULT_TEST)
    p.add_argument("--account",   default=DEFAULT_ACCOUNT)
    p.add_argument("--time",      default=DEFAULT_TIME, help="Wall-clock limit HH:MM:SS")
    p.add_argument("--build-dir", default=DEFAULT_BUILD_DIR)

    args, nccl_args = p.parse_known_args()
    nccl_str = " ".join(nccl_args)

    if args.sweep_nodes:
        node_list = args.sweep_nodes
    elif args.nodes is not None:
        node_list = [args.nodes]
    else:
        p.error("Provide --nodes N or --sweep-nodes N1 N2 ...")

    ok = True
    for n in node_list:
        job_name, script = render_script(n, args.test, args.account,
                                         args.time, args.build_dir, nccl_str)
        try:
            job_id = write_and_submit(job_name, script)
            print(f"[SUBMITTED] {job_name}  →  job id {job_id}")
        except RuntimeError as e:
            print(f"[ERROR]     {job_name}\n{e}", file=sys.stderr)
            ok = False

    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())