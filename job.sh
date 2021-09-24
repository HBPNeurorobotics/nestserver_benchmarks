#!/bin/bash

if [ "$#" -ne 1 ]; then
    echo "Usage: salloc -N 33 -n 66 -c 36 -C mc --hint=multithread -A ich004m --time=20 job.sh <configfile>"
    echo
    echo "-N <num_processes> for the largest benchmark to be run (1 for NRP, N-1 for NEST)"
    echo "-n <num_processes> * 2 and -c 36 to get 2 processes per node and all cores"
    echo "<configfile> is a yaml file that configures the benchmark to be run"
    exit 1
fi

. $HOME/pynrp/bin/activate

configfile=$1
datadir=$(grep 'datadir:' $configfile | cut -d: -f2 | tr -d ' ' | tr -d '"')
datadir=$(eval echo $datadir)
echo $datadir
echo $configfile
nodezero=$(python3 prepare_benchmark.py $configfile)
if [ $? -eq 1 ]; then
    echo "config file error!"
    exit 1
fi

echo "Node zero: $nodezero"

ssh -o StrictHostKeyChecking=no $nodezero bash -s < $datadir/tunnel.sh &
##sleep 10
ssh -o StrictHostKeyChecking=no $nodezero bash -s < $datadir/nrp.sh &

sleep 30 # Give the NRP and tunnel processes time to start

python3 run_benchmark.py $configfile
