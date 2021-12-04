
module load sarus

srun --jobid={jobid} -C mc -A {account} --mpi=pmi2 -v \
     --cpu-bind=threads --distribution=block:cyclic:fcyclic \
     -N {n_nodes_nest} -n {n_tasks_nest} --exclude={nodezero} \
     sarus run \
           --mount=type=bind,source=$HOME,dst=$HOME \
           load/library/nest_latest_daint:latest \
           bash -c ' \
               source /opt/nest/bin/nest_vars.sh; \
	       ln -s {working_dir}/Experiments/RoboBrain_benchmark/1_nrpexperiment_robobrain_mouse/resources /opt/data; \
	       ln -f -s {working_dir}/fixes/hl_api_server.py /opt/nest/lib/python3.8/site-packages/nest/server/hl_api_server.py; \
	       export NEST_SERVER_MODULES="nest,numpy,time,math"; \
	       export NEST_SERVER_RESTRICTION_OFF=true; \
               nest-server-mpi --host 0.0.0.0 --port 5000'
