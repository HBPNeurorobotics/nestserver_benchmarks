
import ruamel.yaml as yaml
import os


def expand_nodelist():
    """Expand the Slurm nodelist.

    This function expects the environment variable SLURM_NODELIST to be set
    and to look something like 'nid0[27,48,50-52]'. In this example case, it
    will return the list ["nid027", "nid048", "nid050", "nid051", "nid052"].

    """
    # print({x:y for x,y in os.environ.items() if "SLURM" in x})
    prefix, rawids = os.environ.get("SLURM_NODELIST").replace("]", "").split("[")
    node_ids = []
    for id_range in rawids.split(","):
        if "-" in id_range:
            a, b = id_range.split("-")
            node_ids += list(range(int(a), int(b) + 1))
        else:
            node_ids.append(int(id_range))
    return [f"{prefix}{id}" for id in node_ids]


def get_config(config_fname):

    with open(config_fname, 'r') as config_file:
        config = yaml.safe_load(config_file)
        homedir = os.environ.get("HOME")
        config['datadir'] = config['datadir'].replace("$HOME", homedir)
        return config

    print(f"Error: config file '{configfile}' could not be read'.\n")
    exit(1)


def get_secrets():

    secrets_fname = "secrets.yaml"

    if not os.path.isfile(secrets_fname):
        print(f"Cannot open 'secrets.yaml'.\n")
        exit(1)

    if oct(os.stat(secrets_fname).st_mode)[-3:] != "600":
        print(f"Error: permissions of 'secrets.yaml' too open. Run 'chmod 600 secrets.yaml'.\n")
        exit(1)

    with open(secrets_fname, 'r') as secrets_file:
        secrets = yaml.safe_load(secrets_file)
        return secrets