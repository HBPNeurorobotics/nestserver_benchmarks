# NRP + NEST Server Benchmark Experiments

This folder contains the code and results of the NRP + NEST Server benchmark
experiments run on Piz Daint and are described in detail in [Feldotto et al.,
2022](XXX).

## Introduction

Running benchmarks with the Neurorobotics Platform and distributed NEST-server
on High Performance Computing resources requires basically three steps:

1. a HPC job has to be allocated using `salloc`
1. the NRP container and the tunnel to the frontend machine have to be run on
   the first node of the allocation
1. the NEST container has to be deployed on all but the first nodes using
   `srun`

The first two steps are independent of the concrete parallelization setup of
NEST, while the last one uses different numbers of nodes, MPI processes, and/or
threads per process for each benchmark step.

## Software and containers

The benchmark runner and analysis/plotting scripts require a number of Python
modules. They are listed in the file `requirements.txt` and can be easily
installed on Piz Daint using

```bash
module load cray-python/3.8.5.1
pip3 install -r requirements.txt
```

The benchmarks are executed using the NRP Virtual Coach
[VirtualCoach](https://bitbucket.org/hbpneurorobotics/virtualcoach), a python
module to script experiment execution.
It can be installed into a Python virtual environment using pip:

```bash
virtualenv pynrp
source pynrp/bin/activate
pip3 install pynrp
```

The environment is activated from within `job.sh` before the actual benchmark
scripts are run.

To install the necessary Docker containers from the EBRAINS harbor registry
the following commands can be used:

```bash
module load sarus
module use /scratch/snx3000/bignamic/EasyBuildInstall/modules/all/
module load skopeo

skopeo copy --insecure-policy \
       docker://docker-registry.ebrains.eu/nrp-daint/nrp@sha256:2e249d2a3cfd3d6df27fded8a03b5d74e9f485e4de4249648ccdea3dfce9587e \
       docker-archive:nrp_nest_client.tar
sarus load nrp_nest_client.tar nrp_nest_client

skopeo copy --insecure-policy \
       docker://docker-registry.ebrains.eu/nrp-daint/nest_server@sha256:68e9c269f31f2c7a72a8c01497a130971bff0cf1681bce4f96e7fdb335054ff7 \
       docker-archive:nest_latest_daint.tar
sarus load nest_latest_daint.tar nest_latest_daint
```

## EBRAINS credentials

Logging into the HBP Neurorobotics Platform via VirtualCoach requires EBRAINS
credentials. To keep these safe and separate from the benchmark configuration,
they are stored in `secrets.yaml`, which has to be only user-readable (600)
and look like this:

```yaml
hbp_username: "your_ebrains_username"
hbp_password: "your_ebrains_password"
```

For your convenience, a template of the file is available in the repository
under the name `secrets.yaml.ini`. You can copy that file to `secrets.yaml`
and modify it as needed. The file will subsequently be ignored by Git, as to
not add it to the repository by accident.

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

All parameter configurations for the benchmark runs can be found in the
config.yaml file.


## Main job script

We run experiments in batches, that means every benchmark experiment run
is executed x times in order to prove reproducibility of results.
Benchmark experiment runs can be started with the following command, passing
the configuration file to the batch run script:

./batch config.yaml

The main runner of an individual benchmark run is implemented in `job.sh`.
It will first check commandline arguments, call the `prepare_benchmark.py`
script to templatize the secondary run scripts and then run them on the first
node of the allocation using `ssh`. After a short waiting time to let the NRP
and the tunnel become available, it starts the main loop that is contained in
`run_benchmark.sh`.

Please note that even thought the allocation is set up so that it provides the
right amount of nodes and space for the right amount of processes per node and
threads per process, it is still important to tell NEST to use 36 threads per
process. This is done by setting the kernel property `local_num_threads` to 36
either during the call to `startup()` from within the CLE or from within the
brain simulation script itself.

## Plotting and analysis

The result data generated by job runs can be plotted by the script
`process_benchmark_data.py RESULT_FOLDER`. It can be supplied with the name
of a result data directory generated from an benchmark batch run. Generated
diagrams are dropped in a dedicated diagrams folder of the benchmark run results.
An example invocation looks like this:

```bash
python3 process_benchmark_data.py Results_paper/3_robobrain/2022-02-03_12-03-15-robobrain_fullbrain
```

Two additional scripts can be found in this repository that have been implemented
to generate the figures of the referenced paper, `create_paper_figures.py` to
assemble multiple diagrams of a benchmark run, and `create_comparison.py` to
generate a comparison figure of different benchmark runs.


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
`HPC_benchmark`), and an embodied multi-region rodent brain simulation
(directory `RoboBrain`).

The benchmarks are explained in more detail in the referenced paper.
