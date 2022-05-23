#! /bin/bash

module load sarus

export NRPLOGDIR=/users/bp000231/bf_data/nestserver_benchmarks/tmp_benchmarks_results/2021-11-25_18-15-04-hpcbench_notf/3/nrplogs

mkdir -p $NRPLOGDIR/nginx
mkdir -p $NRPLOGDIR/nrp-services_app
mkdir -p $NRPLOGDIR/ros-simulation-factory_app
mkdir -p $NRPLOGDIR/rosbridge
mkdir -p $NRPLOGDIR/roscore
mkdir -p $NRPLOGDIR/rosvideoserver
mkdir -p $NRPLOGDIR/virtualcoach
mkdir -p $NRPLOGDIR/uwsgi
mkdir -p $NRPLOGDIR/nginx_home

export NRPSRC=/home_daint/bbpnrsoa/nrp/src
export NRPSRCCOMM=$NRPSRC/ExDBackend/hbp_nrp_commons/hbp_nrp_commons
export NRPSRCSERV=$NRPSRC/ExDBackend/hbp_nrp_cleserver/hbp_nrp_cleserver
export NRPSRCLNCH=$NRPSRC/BrainSimulation/hbp_nrp_distributed_nest/hbp_nrp_distributed_nest/launch
export NRPVARLOG=/var/log/supervisor

sarus run \
      --mount=type=bind,source=/etc/opt/slurm/slurm.conf,dst=/usr/local/etc/slurm.conf \
      --mount=type=bind,source=/var/run/munge/munge.socket.2,dst=/var/run/munge/munge.socket.2 \
      --mount=type=bind,source=$HOME,dst=$HOME \
      --mount=type=bind,source=$NRPLOGDIR/nginx,dst=$NRPVARLOG/nginx \
      --mount=type=bind,source=$NRPLOGDIR/nrp-services_app,dst=$NRPVARLOG/nrp-services_app \
      --mount=type=bind,source=$NRPLOGDIR/ros-simulation-factory_app,dst=$NRPVARLOG/ros-simulation-factory_app \
      --mount=type=bind,source=$NRPLOGDIR/rosbridge,dst=$NRPVARLOG/rosbridge \
      --mount=type=bind,source=$NRPLOGDIR/roscore,dst=$NRPVARLOG/roscore \
      --mount=type=bind,source=$NRPLOGDIR/rosvideoserver,dst=$NRPVARLOG/rosvideoserver \
      --mount=type=bind,source=$NRPLOGDIR/virtualcoach,dst=$NRPVARLOG/virtualcoach \
      --mount=type=bind,source=$NRPLOGDIR/uwsgi,dst=$NRPVARLOG/uwsgi \
      --mount=type=bind,source=$NRPLOGDIR/nginx_home,dst=/home_daint/bbpnrsoa/nginx \
      \
      nexus.neurorobotics.ebrains.eu/daint/nrp:3.2.0-nest-client \
      \
      bash -c "\
          unset LD_PRELOAD; \
          export LD_LIBRARY_PATH=/usr/lib:$LD_LIBRARY_PATH; \
          export LC_ALL=C; unset LANGUAGE; \
          source $NRPSRC/user-scripts/nrp_variables; \
	  sed -i 's|self.__remaining_time = timeout|self.__remaining = timeout|' $NRPSRC/ExDBackend/hbp_nrp_cleserver/hbp_nrp_cleserver/server/SimulationServer.py; \
          sed -i 's|<STORAGE_ADDR>|148.187.148.14|' $NRPSRCCOMM/workspace/Settings.py; \
          sed -i 's|= MPILauncher|= DaintLauncher|' $NRPSRCLNCH/NestLauncher.py; \
          sed -i 's|sys.executable|\\\"/home_daint/bbpnrsoa/.opt/platform_venv/bin/python\\\"|' $NRPSRCLNCH/NestLauncher.py; \
          sed -i 's|$VGLRUN|xvfb-run -a --server-args=\\\"-screen 0 1280x1024x24\\\"|' /home_daint/bbpnrsoa/.opt/bbp/nrp-services/gzserver; \
          sed -i 's|resolver 8.8.8.8;|resolver 148.187.18.88;|' /home_daint/bbpnrsoa/.local/etc/nginx/conf.d/nrp-services.conf; \
          sed -i 's|--pause|--pause --software_only_rendering|' /home_daint/bbpnrsoa/.opt/bbp/nrp-services/gzserver; \
          sed -i 's|NestClientControlAdapter()|NestClientControlAdapter(\"nid00216\", 5000)|' $NRPSRCSERV/server/ServerConfigurations.py;
          \
          /etc/init.d/supervisor start;
          sleep infinity;"
