
import ruamel.yaml as yaml
from copy import copy
import sys
import os

import helpers

config_fname = sys.argv[1]
config = helpers.get_config(config_fname)
datadir = config["datadir"]

if os.path.exists(datadir):
    print(f"Error: Output directory '{datadir}' already exists. Please move it out of the way.\n")
    sys.exit(1)

os.makedirs(datadir)

nodelist = helpers.expand_nodelist()

values = {
    "nest_master_node": nodelist[1],
    "nrplogdir": f"{datadir}/nrplogs",
    "tunnel_keyfile": config['tunnel_keyfile'],
    "tunnel_ip": config['tunnel_ip'],
}

for script_basename in ("nrp", "tunnel"):
    with open(f"misc/{script_basename}.sh.tpl", "r") as infile:
        with open(f"{datadir}/{script_basename}.sh", "w") as outfile:
            outfile.write(f"{infile.read()}".format(**values))

print(nodelist[0])
