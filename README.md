# NRP NESTServer Benchmark Experiments

This folder contains the code and results of the NRP + Nest Server
benchmark experiments that were run on Piz Daint and are described in
detail in [Feldotto et al., 2021](XXX).

## Allocate jobs for the benchmarks

When using `salloc` to run the backend services for the benchmarks, a
number of options have to be set:

* the number of nodes to allocate (option `--nodes $NNODES`)
* the number of tasks to run in total (option `--ntasks $NTASKS`
* the partition to use (`--constraint 'mc&startx'`)
* the account to run from (option `--account $ACCOUNT`)
* the time for the job in minutes (`--time 1200`)

Large memory machines (i.e., having 128 GB) can be obtained by
additionally specifying `--mem=120GB`. More details can be found in
the [`salloc` man page](https://slurm.schedmd.com/salloc.html].

In summary, a good starting point for allocating a job is the
following little code snippet:

```bash
JOBNAME='nrp-nest-scaleout'
ACCOUNT='ich004m'
NNODES=2
NTASKS=$(expr $NNODES * 2)
salloc -J $JOBNAME --constraint 'mc&startx' --account $ACCOUNT --time=10 \
	   --nodes $NNODES --ntasks $NTASKS --cpus-per-task 2
```

## Run NEST

After allocation, the NEST container has to be run using `srun`. In
order to use the maximum number of cores on each of the compute nodes
and get the most efficient process/thread layout (i.e., one process
per socket and as many threads as there are [virtual] cores), the
following options have to supplied:

* the number of nodes to use (option `--nodes $(expr $NNODES - 1)` to
  leave one node for the NRP supervisor
* the number of tasks to run (option `--nodes $(expr $NTASKS - 2)`
* the number of tasks per node (option `--ntasks-per-node 2`)
* `--mem-bind local` gives better thread locality of data
* `--hint compute_bound` assigns one thread per core
* `--mpi pmi2` makes sure we're getting the correct MPI type

The corresponding line should look something like this:

```bash
srun --job-name $JOBNAME --mem-bind local --hint compute_bound --mpi pmi2 \
     --nodes $(expr $NNODES - 1) --ntasks $(expr $NTASKS - 2) --ntasks-per-node 2 \
     sarus run \
           --mount=type=bind,source=$HOME,dst=$HOME \
           christopherbignamini/nest:jougs_nest_server_mpi \
           bash -c '\
               if [ $SLURM_PROCID -eq 0 ]; \
                 then hostname > $HOME/nest_master_node_id; \
               fi; \
               source /opt/nest/bin/nest_vars.sh; \
               nest-server-mpi --host 0.0.0.0 --port 5000'
```

It is still important to tell NEST to use 36 threads per process by
setting the kernel property `local_num_threads` to 36 either during
the call to `startup()` from within the CLE or from within the brain
simulation script.

## Run the thread pinning tester

A small test program to check the pinning of threads to CPUs/cores is
available in `misc/`. It can be compiled using

```
cd misc
gcc -fopenmp omp_test.c
```

After compilation, it can be run using
```
srun --nodes 2 --ntasks 4 --ntasks-per-node=2 \
     --mem-bind=local --hint=compute_bound ./a.out
```

## Run the BENCHMARKS

The benchmark experiments can be run with the VirtualCoach script
vc_run_benchmarks.py.


## Benchmark experiment description


### HPC Benchmark

TODO: Describe HPC model here

#### no TF no model
TODO: Describe benchmark experiment here

#### data readout no model
TODO: Describe benchmark experiment here


## RoboBrain Benchmark
TODO: Describe RoboBrain model here

#### brain, TF, body
TODO: Describe benchmark experiment here
