# NRP + NEST Server Benchmark Experiments

This folder contains the code and results of the NRP + NEST Server benchmark
experiments run on Piz Daint and are described in detail in [Feldotto et al.,
2021](XXX).

## Introduction

Due to the many parts of the HBP Neurorobotics Platform, running benchmarks on
it is not completely trivial and requires a number of steps:

1. a job has to be allocated using `salloc`
1. the NRP container and the tunnel to the frontend machine have to be run on
   the first node of the allocation
1. the NEST container has to be deployed on all but the first nodes using
   `srun`

The first three steps are independent of the concrete parallelization setup of
NEST, while the last one uses different numbers of nodes, MPI processes, and/or
threads per process for each benchmark step.

## Software and containers

VirtualCoach can be installed into a Python virtual environment using the
following sequence of commands:

```bash
virtualenv pynrp
source pynrp/bin/activate
pip3 install pynrp
```

The environment is activated from within `job.sh` before the actual benchmark
scripts are run.

To install the necessary Docker containers, the following commands can be
used:

```bash
module load sarus
sarus pull christopherbignamini/nest:jougs_nest_server_mpi

module use /scratch/snx3000/bignamic/EasyBuildInstall/modules/all/
module load skopeo
skopeo copy --insecure-policy \
       docker://docker-registry.ebrains.eu/nrp-daint/nrp@sha256:1dfbe38dae84393402d30e1921cdf2f690beece62498389194ececc6a3aa525b \
       docker-archive:nrp_nest_client.tar
sarus load nrp_nest_client.tar nrp_nest_client
```

## Job allocation

In order to obtain a somewhat stable environment for running the benchmarks
and thus increase the comparability between different runs, we allocate the
maximum required number of nodes right from the start. The different benchmark
steps will then only use a certain portion of nodes for the points they want
to measure.

All benchmarks are run such that the NRP backend services (supervisor and
tunnel) are run on one node and NEST is run on the remainder of the nodes.
This results in slightly unconventional allocation sizes that are always one
larger than the next power-of-two number would be.

A number of options have to be supplied to `salloc` to obtain the allocation:

* **`--nodes $NNODES`**: the total number of nodes to allocate: set to the
  maximum desired number of nodes for NEST plus one
* **`--ntasks $NTASKS`**: the total number of tasks in the allocation: set to
  the number of nodes times two
* **`--cpus-per-task 36`**: the number of cpus per task: setting to 36 unlocks
  all available hardware threads
* **`--constraint mc`**: the partition to use
* **`--account $ACCOUNT`**: the account to run from
* **`--time 1200`**: the maximum wallclock time for the job in minutes: this
  can be set generously, as the job will end when all benchmarks are done.

Large memory machines (i.e., having 128 GB) can be obtained by additionally
specifying `--mem=120GB`. More detailed information on the options can be
found in the [`salloc` man page](https://slurm.schedmd.com/salloc.html].

The following snippet of bash code is a good starting point for allocating a
job for running the benchmarks

```bash
salloc --constraint mc -A ich004m --time=200 \
       --nodes 33 --ntasks 66 --cpus-per-task 36 --hint=multithread \
       job.sh config.yaml
```

## Main job script

The main runner for the benchmarks is implemented in `job.sh`. It will first
check commandline arguments, call the `prepare_benchmark.py` script to
templatize the secondary run scripts and then run them on the first node of
the allocation using `ssh`. After a short waiting time to let the NRP and the
tunnel become available, it starts the main loop that is contained in
`run_benchmark.sh`.

Please note that even thought the allocation is set up so that it provides the
right amount of nodes and space for the right amount of processes per node and
threads per process, it is still important to tell NEST to use 36 threads per
process. This is done by setting the kernel property `local_num_threads` to 36
either during the call to `startup()` from within the CLE or from within the
brain simulation script itself.

## Thread pinning tester

A small test program to check the pinning of threads to CPUs/cores is
available in `misc/`. It can be compiled using

```bash
gcc -fopenmp -o omp_test omp_test.c
```

and run using
```bash
srun --nodes 2 --ntasks 4 --ntasks-per-node=2 \
     --mem-bind=local --hint=compute_bound ./omp_test
```

## Benchmark experiments

The benchmark suite consists of two main components: a rather synthetic (but
well controllable) brain simulation test case in the form of a [random
balanced network](http://www.yger.net/the-balanced-network/) (directory
`HPC_benchmark`), and a robotic simulation coupled with a motor-cortex brain
simulation (directory `RoboBrain`)

The benchmarks are explained in more detail in the corresponding directories.
