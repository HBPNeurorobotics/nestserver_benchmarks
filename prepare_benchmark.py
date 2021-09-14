
import ruamel.yaml as yaml
from copy import copy
import sys
import os

import helpers

config_fname = sys.argv[1]
config = helpers.get_config(config_fname)

if os.path.isdir(config["datadir"]):
    print(f"Error: Output directory '{datadir}' already exists.\n")
    sys.exit(1)

os.makedirs(config["datadir"])

with open(f"{config['datadir']}/{config_fname}", 'w') as config_file:
    config_pwless = copy(config)
    config_pwless["hbp_password"] = "********"
    config_file.write(yaml.dump(config_pwless, default_flow_style=False))

nodelist = helpers.expand_nodelist()

values = {
    "nest_master_node": nodelist[1],
    "nrplogdir": f"{config['datadir']}/nrplogs",
    "tunnel_keyfile": config['tunnel_keyfile'],
    "tunnel_ip": config['tunnel_ip'],
}

for script_basename in ("nrp", "tunnel"):
    with open(f"misc/{script_basename}.sh.tpl", "r") as infile:
        with open(f"{config['datadir']}/{script_basename}.sh", "w") as outfile:
            outfile.write(f"{infile.read()}".format(**values))

print(nodelist[0])
