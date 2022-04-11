
module load sarus

srun --jobid=34330167 -C mc -A ich004m --mpi=pmi2 -v \
     --cpu-bind=threads --distribution=block:cyclic:fcyclic \
     -N 8 -n 16 --exclude=nid01411 \
     sarus run \
           --mount=type=bind,source=$HOME,dst=$HOME \
           christopherbignamini/nest:jougs_nest_server_mpi \
           bash -c '\
               source /opt/nest/bin/nest_vars.sh; \
               nest-server-mpi --host 0.0.0.0 --port 5000'
