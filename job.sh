#!/bin/bash

if [ "$#" -ne 2 ]; then
    echo "Usage: salloc -N 33 -n 66 -c 36 -C mc -A ich004m --time=1 job.sh <configfile> <rundir>"
    echo
    echo "-N <num_processes> for the largest benchmark to be run (1 for NRP, N-1 for NEST)"
    echo "-n <num_processes> * 2 and -c 36 to get 2 processes per node and all cores"
    echo "<configfile> is a yaml file that configures the benchmark to be run"
    echo "<rundir> current run directory for results"
    exit 1
fi

. $HOME/pynrp/bin/activate

configfile=$1
rundir=$2

nodezero=$(python3 prepare_benchmark.py $configfile $rundir)

echo nodezero is $nodezero

if [ $? -eq 1 ]; then
    echo $nodezero
    echo
    exit 1
fi

cp $configfile $rundir/config.yaml

echo "Node zero: $nodezero"

ssh -o StrictHostKeyChecking=no $nodezero bash -s < $rundir/../tunnel.sh &
ssh -o StrictHostKeyChecking=no $nodezero bash -s < $rundir/../nrp.sh &
sleep 15 # Give the NRP and tunnel processes time to start

python3 run_benchmark.py $configfile $rundir
