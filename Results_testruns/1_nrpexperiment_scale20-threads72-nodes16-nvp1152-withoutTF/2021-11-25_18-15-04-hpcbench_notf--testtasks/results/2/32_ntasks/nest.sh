
module load sarus

srun --jobid=35163742 -C mc -A ich004m --mpi=pmi2 -v \
     --cpu-bind=threads --distribution=block:cyclic:fcyclic \
     -N 32 -n 64 --exclude=nid00215 \
     sarus run \
           --mount=type=bind,source=$HOME,dst=$HOME \
           load/library/nest_latest_daint:latest \
           bash -c '\
               source /opt/nest/bin/nest_vars.sh; \
               nest-server-mpi --host 0.0.0.0 --port 5000'
