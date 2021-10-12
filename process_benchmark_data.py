from matplotlib import pyplot as plt
import ruamel.yaml as yaml
from pprint import pprint
import sys

base_font_size = 12
plt.rc('font', size=base_font_size)
plt.rc('axes', titlesize=base_font_size + 4)
plt.rc('axes', labelsize=base_font_size + 2)
plt.rc('axes.spines', top=False, right=False, bottom=False, left=False)
plt.rc('xtick', labelsize=base_font_size, color='#666')
plt.rc('ytick', labelsize=base_font_size, color='#666')
plt.rc('legend', fontsize=base_font_size)
plt.rc('axes', facecolor='white', titlecolor='#666')
plt.rc('grid', color='gray', ls='dotted')

labels = {
    "hpcbench_notf": "NRP+NEST, no TF",
    "hpcbench_readspikes": "NRP+NEST, spike-reading TF",
    "hpcbench_baseline": "NEST standalone",
}


class BenchmarkProcessor:

    def __init__(self):

        self.data = {}
        for i, datadir in enumerate(sys.argv[1:]):
            config = self.read_yaml_file(f"{datadir}/config.yaml")
            key = f"{i:02d}-{config['testcase']}"
            self.data[key] = {
                "config": config,
                # "metadata": self.read_yaml_file(f"{datadir}/metadata.yaml"),
                "data": {"numnodes": config["n_nodes"]}
            }
            self.read_run_data(datadir, config, self.data[key]["data"])
            self.get_linear_expectation(self.data[key]["data"])

        pprint(self.data)

    def read_yaml_file(self, fname):
        with open(fname, 'r') as config_file:
            return yaml.safe_load(config_file)

    def read_run_data(self, datadir, config, data):
        data["metadata"] = []
        data["runtimes"] = []
        for n in config["n_nodes"]:
            read_func = getattr(self, f"read_{config['testcase']}_data")
            rundir = f"{datadir}/{n:02d}nodes"
            read_func(rundir, n, data)

    def read_hpcbench_notf_data(self, rundir, n, data):
        # data["metadata"].append(self.read_yaml_file(f"{rundir}/metadata.yaml"))
        with open(f"{rundir}/total_time.dat", "r") as datafile:
            data["runtimes"].append(float(datafile.read()))

    def read_hpcbench_baseline_data(self, rundir, n, data):
        data["metadata"].append(self.read_yaml_file(f"{rundir}/metadata.yaml"))
        with open(f"{rundir}/total_time.dat", "r") as datafile:
            data["runtimes"].append(float(datafile.read()))

    def get_linear_expectation(self, data):
        factors = [n/data["numnodes"][0] for n in data["numnodes"]]
        data["linear"] = [data["runtimes"][0]/f for f in factors]

    def print_network_creation_time(self):
        pass

    def create_memory_plot(self):
        pass

    def create_profiler_runtime_plot(self):
        pass


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <datadir1> [<datadir2> ...]")
    processor = BenchmarkProcessor()

    plt.figure(figsize=[8, 6])

    xticks = set()
    for i, (run, data) in enumerate(processor.data.items()):
        d = data["data"]
        x = d["numnodes"]
        plt.plot(x, d["runtimes"], lw=2, c=f"C{i}", label=labels[run[3:]])
        plt.plot(x, d["linear"], lw=4, c=f"C{i}", alpha=0.25)
        for n in d["numnodes"]:
            xticks.add(n)
        # TODO: get number of neurons and connections from metadata and use in
        # subtitle

    title = "Coupled NRP+NEST HPC benchmark simulation"
    subtitle = f"225K neurons, 39M connections"
    plt.title(f'{title}\n{subtitle}')
    plt.setp(plt.legend().get_texts(), color='#666')
    plt.xlabel('number of compute nodes', color='#666')
    plt.xticks(list(xticks))
    plt.ylabel('total run time (s)', color='#666')
    plt.grid(True, axis='y')
    plt.tight_layout(pad=0.25, w_pad=0.25, h_pad=0.25)
    plt.savefig(f'figure.pdf')
