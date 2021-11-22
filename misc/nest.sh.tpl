
module load sarus

srun --jobid={jobid} -C mc -A {account} --mpi=pmi2 -v \
     --cpu-bind=threads --distribution=block:cyclic:fcyclic \
     -N {n_nodes_nest} -n {n_tasks_nest} --exclude={nodezero} \
     sarus run \
           --mount=type=bind,source=$HOME,dst=$HOME \
           load/library/nest_latest_daint:latest \
           bash -c '\
               source /opt/nest/bin/nest_vars.sh; \
               nest-server-mpi --host 0.0.0.0 --port 5000'
