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

The benchmark runner and analysis/plotting scripts require a number of Python
modules. They are listed in the file `requirements.txt` and can be easily
installed using

```bash
module load cray-python/3.8.5.1
pip3 install -r requirements.txt
```

The benchmarks runs using the NRP are run using the commandline interface
[VirtualCoach](https://bitbucket.org/hbpneurorobotics/virtualcoach). It can be
installed into a Python virtual environment using the following sequence of
commands:

```bash
virtualenv pynrp
source pynrp/bin/activate
pip3 install pynrp

cd pynrp/lib64/python3.6/site-packages/pynrp
vp_url="https://bitbucket.org/hbpneurorobotics/virtualcoach"
vp_githash="b4d8c119170a89621ffb298ba47a0345d7b0c7ae"
vp_path="hbp_nrp_virtual_coach/pynrp"
for file in config.json config.py virtual_coach.py; do
  wget -o $file $vp_url/$vp_githash/$vp_path/$file
done
```

The environment is activated from within `job.sh` before the actual benchmark
scripts are run.

To install the necessary Docker containers, the following commands can be
used:

```bash
module load sarus
module use /scratch/snx3000/bignamic/EasyBuildInstall/modules/all/
module load skopeo

skopeo copy --insecure-policy \
       docker://docker-registry.ebrains.eu/nrp-daint/nrp@sha256:caadd07080aa455c8c0ed4139117136f5d0a209aac0ad6d547108c06a683acbf \
       docker-archive:nrp_nest_client.tar
sarus load nrp_nest_client.tar nrp_nest_client

skopeo copy --insecure-policy \
       docker://docker-registry.ebrains.eu/nest/nest-simulator@sha256:1b717264545522a18502d6e784e3a4a049fcfd20a182cca9e653bb60944e033d \
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

The following snippet of bash code is a good starting point for allocating a
job for running the benchmarks

```bash
salloc --constraint mc -A ich004m --time=200 \
       --nodes 33 --ntasks 66 --cpus-per-task 36 --hint=multithread \
       job.sh config.yaml
```

The allocation can be triggered with the bash.sh skript. In here it is possible 
execute multiple repetitions of the same benchmark run.

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

## Plotting and analysis

The result data generated by job runs can be plotted by the script
`process_benchmark_data.py`. It can be supplied with the names of one or more
data directories. An example invocation looks like this:

```bash
python3 process_benchmark_data.py data_notf data_baseline
```

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
