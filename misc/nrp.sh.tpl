#! /bin/bash

module load sarus

export NRPLOGDIR={nrplogdir}

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
      load/library/nrp_nest_client:latest \
      \
      bash -c "\
          unset LD_PRELOAD; \
          export LD_LIBRARY_PATH=/usr/lib:$LD_LIBRARY_PATH; \
          export LC_ALL=C; unset LANGUAGE; \
          source $NRPSRC/user-scripts/nrp_variables; \
          sed -i 's|<STORAGE_ADDR>|148.187.96.212|' $NRPSRCCOMM/workspace/Settings.py; \
          sed -i 's|= MPILauncher|= DaintLauncher|' $NRPSRCLNCH/NestLauncher.py; \
          sed -i 's|sys.executable|\\\"/home_daint/bbpnrsoa/.opt/platform_venv/bin/python\\\"|' $NRPSRCLNCH/NestLauncher.py; \
          sed -i 's|$VGLRUN|xvfb-run -a --server-args=\\\"-screen 0 1280x1024x24\\\"|' /home_daint/bbpnrsoa/.opt/bbp/nrp-services/gzserver; \
          sed -i 's|--pause|--pause --software_only_rendering|' /home_daint/bbpnrsoa/.opt/bbp/nrp-services/gzserver; \
	  sed -i 's|NestClientControlAdapter()|NestClientControlAdapter(\"{nest_master_node}\", 5000)|' $NRPSRCSERV/server/ServerConfigurations.py;
          \
          /etc/init.d/supervisor start;
	  sleep infinity;"
