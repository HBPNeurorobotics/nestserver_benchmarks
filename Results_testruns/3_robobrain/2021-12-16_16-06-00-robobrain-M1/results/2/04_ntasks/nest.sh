
module load sarus

srun --jobid=35533300 -C mc -A ich004m --mpi=pmi2 -v \
     --cpu-bind=threads --distribution=block:cyclic:fcyclic \
     -N 2 -n 4 --exclude=nid01358 \
     sarus run \
           --mount=type=bind,source=$HOME,dst=$HOME \
           load/library/nest_latest_daint:latest \
           bash -c ' \
               source /opt/nest/bin/nest_vars.sh; \
	       ln -s /users/bp000231/bf_data/nestserver_benchmarks/Experiments/RoboBrain_benchmark/1_nrpexperiment_robobrain_mouse/resources /opt/data; \
	       cp /users/bp000231/bf_data/nestserver_benchmarks/fixes/hl_api_server.py /opt/nest/lib/python3.8/site-packages/nest/server/hl_api_server.py; \
	       echo BF nest server dir is; \
	       ls /opt/nest/lib/python3.8/site-packages/nest/server; \
	       export NEST_SERVER_MODULES="nest,numpy,time,math"; \
	       export NEST_SERVER_RESTRICTION_OFF=true; \
               nest-server-mpi --host 0.0.0.0 --port 5000'
