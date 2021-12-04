
module load sarus

srun --jobid=35302130 -C mc -A ich004m --mpi=pmi2 -v \
     --cpu-bind=threads --distribution=block:cyclic:fcyclic \
     -N 2 -n 4 --exclude=nid00275 \
     sarus run \
           --mount=type=bind,source=$HOME,dst=$HOME \
           load/library/nest_latest_daint:latest \
           bash -c '\
	       ln -s $HOME/bf_data//nestserver_benchmarks/Experiments/RoboBrain_benchmark/1_nrpexperiment_robobrain_mouse/resources /opt/data; \
	       echo BFFFFFF; \
	       ls /opt/data; \
	       export NEST_SERVER_MODULES="nest,numpy,time,math"; \
               export NEST_SERVER_RESTRICTION_OFF=true; \
	       source /opt/nest/bin/nest_vars.sh; \
               nest-server-mpi --host 0.0.0.0 --port 5000'
