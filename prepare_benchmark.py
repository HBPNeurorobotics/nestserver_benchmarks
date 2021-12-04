
import ruamel.yaml as yaml
from copy import copy
import sys
import os
from datetime import datetime

import helpers


# Load config file
config_fname = sys.argv[1]
config = helpers.get_config(config_fname)


# Create results folder for run
rundir = sys.argv[2]
os.makedirs(rundir)


# Retrieve Nodelist
nodelist = helpers.expand_nodelist()


# Collect parameter for NRP and tunnel
values = {
    "nest_master_node": nodelist[1],
    "nrplogdir": f"{rundir}/nrplogs",
}

for key in ("tunnel_keyfile", "tunnel_ip", "tunnel_port"):
    values[key] = config[key]
values["working_dir"] = os.getcwd()

# Generate NRP and tunnel scripts
for script_basename in ("nrp", "tunnel"):
    with open(f"misc/{script_basename}.sh.tpl", "r") as infile:
        with open(f"{rundir}/../{script_basename}.sh", "w") as outfile:
            outfile.write(f"{infile.read()}".format(**values))


# Return nodelist and results directory
print(nodelist[0])
