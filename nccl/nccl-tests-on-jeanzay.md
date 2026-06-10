# Why

Running [`nccl-tests`](https://github.com/NVIDIA/nccl-tests) on a machine gives us performance expectations for P2P and collectives in our HPC apps.

# Building the tests on JeanZay

In order to build the tests with MPI enabled (as we want to scale to several nodes), we load mpi (no need for cuda aware) as well as nccl, then follow the build instructions. It is important to build the tests on the compute nodes, are they are separate from the login nodes

# Figuring out the topology of a H100 node

# Results



## Bandwitdh

## Latency

## Troubleshooting performance issues 

I saw good performance on all reduce on one node (300GB/s), dropping sharply on 2 nodes to 4GB/s, versus 25-50GB/s expected with IB.


With the debug info (`export NCCL_DEBUG=INFO`), we get:
```bash 
#First, the rdma driver is not found:

libibverbs: Warning: couldnt load driver 'libmlx5-rdmav34.so': libmlx5-rdmav34.so: cannot open shared object file: No such file or directory


jzxh330:85602:85602 [0] NCCL INFO dlvsym failed on mlx5dv_get_data_direct_sysfs_path - /lustre/fshomisc/sup/spack_soft/rdma-core/52.0/gcc-11.5.0-wmy3e3sjbczjxoozt3dhzwevf5b2u2d3/lib64/libmlx5.so.1: undefined symbol: mlx5dv_get_data_direct_sysfs_path, version MLX5_1.25 version MLX5_1.25

#dlvsym fails to load a symbol from rdma-core this disables IB.

[...]

jzxh330:85602:85602 [0] NCCL INFO NET/IB : No device found.
jzxh330:85602:85602 [0] NCCL INFO NET/IB : Using [RO]; OOB ibp24s0:10.100.9.37<0>
jzxh330:85602:85602 [0] NCCL INFO Failed to initialize NET plugin IB
#As a result, no IB device is detected and IB is no used as a protocol, despite ib interfaces (hardware) being detected.
[...]

jzxh331:86341:86341 [0] NCCL INFO NET/Plugin: Could not find: libnccl-net.so
jzxh330:85602:85602 [0] NCCL INFO NET/Socket : Using [0]ibp24s0:10.100.9.37<0> [1]ibp41s0:10.100.9.38<0> [2]ibp154s0:10.100.9.39<0> [3]ibp170s0:10.100.9.40<0>
jzxh330:85602:85602 [0] NCCL INFO Initialized NET plugin Socket
jzxh330:85605:85605 [0] NCCL INFO Assigned NET plugin Socket to comm

#IB being off, fallback TCP protocol is used, on ib hardware

jzxh331:86341:86341 [0] NCCL INFO NET/Socket : GPU Direct RDMA Disabled for HCA 0 'ibp24s0'

# Since IB is off, and TCP does not support direct RDMA, it's off too
```

Therefore, internode comm do GPU → Host RAM → HCA → Network instead of GPU → HCA → Network, very poor perf.

The fix ? TDB

# Glossary

- **HSA:**  A Host Channel Adapter is a network interface used in high-performance computing (HPC) systems to connect servers to high-speed interconnects such as InfiniBand.
- **InfiniBand:** InfiniBand (IB) is a computer networking standard used in high-performance computing that features very high throughput and very low latency. It is used for data interconnect both among and within computers. InfiniBand is also used as either a direct or switched interconnect between servers and storage systems, as well as an interconnect between storage systems.
- **TCP:** Transmission Control Protocol. In distributed GPU training, TCP protocol is often used for Fallback communication when high-performance protocols are unavailable, even on the corresponding high performance hardware. As a protocol, it is much slower than Infiniband.
- **[rdma-core](https://github.com/linux-rdma/rdma-core):** This is the userspace components for the Linux Kernel's drivers/infiniband subsystem. Specifically this contains the userspace libraries for the following device nodes:
- **dlvsym** Obtain the address of a symbol from a dlopen object, e.g. loads a symbol from a shared library.
- **libiverb:** libibverbs is a library that allows programs to use RDMA "verbs" for direct access to RDMA (currently InfiniBand and iWARP) hardware from userspace. 
- **NIC** Network interface card, It enables data to be sent and received between the computer and other network-connected devices
- **SMP** Symmetric Multiprocessing, On modern multi-socket servers, it refers to the interconnect that connects different CPU sockets (NUMA nodes) together.
- **NVME:** Storage device (sometime on nodes)