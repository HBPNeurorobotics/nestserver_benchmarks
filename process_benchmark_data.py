from matplotlib import pyplot as plt
import ruamel.yaml as yaml
from pprint import pprint
import sys
import os
import logging
import glob
import pandas as pd
import time

# Plot parameter
base_font_size = 12
figsize = [8, 6]
plt.rc('font', size=base_font_size)
plt.rc('axes', titlesize=base_font_size + 4)
plt.rc('axes', labelsize=base_font_size + 2)
plt.rc('axes.spines', top=False, right=False, bottom=False, left=False)
plt.rc('xtick', labelsize=base_font_size, color='#666')
plt.rc('ytick', labelsize=base_font_size, color='#666')
plt.rc('legend', fontsize=base_font_size)
plt.rc('axes', facecolor='white', titlecolor='#666')
plt.rc('grid', color='gray', ls='dotted')

cle_profiler_columns = ['robot_step', 'brain_step', 'brain_refresh', 'cle_step']

labels = {
    "hpcbench_baseline": "NEST standalone",
    "hpcbench_notf": "NRP+NEST, no TF",
    "hpcbench_readspikes": "NRP+NEST, spike-reading TF",
    "robobrain": "RoboBrain experiment"
}


class BenchmarkProcessor:

    def __init__(self):
        """
        Initialize Benchmark Data processor
        """

        # Set up logging
        FORMAT = '[%(asctime)-15s - %(user)-8s] %(message)s'
        logging.basicConfig(format=FORMAT)
        self.logger = logging.getLogger('BenchmarkRunner')
        logging.basicConfig(level = logging.INFO)

        # collected data
        self.data = {}


    def process_data_runs(self, data_dir_nr, data_dir):
        """
        Processes all repetitions and its runs in the given datadir
        """

        self.logger.info("Process Data")

        # create diagrams Folder
        results_folder = os.path.join(data_dir, 'results')
        diagram_folder = os.path.join(data_dir, 'diagrams')
        os.makedirs(diagram_folder, exist_ok=True)

        # generate new data key for data folder
        config = self.read_yaml_file(f"{results_folder}/config.yaml")
        key = f"{config['testcase']}-{data_dir_nr:02d}"
        self.data[key] = {
            "config": config,
            # "metadata": self.read_yaml_file(f"{datadir}/metadata.yaml"),
            "data": {}
        }

        for repetition_folder in [os.path.basename(folder[:-1]) for folder \
                                  in glob.glob(results_folder + "/*/")]:
            # loop for all repetitions in data dir
            repetition_path = os.path.join(results_folder, repetition_folder)
            self.data[key]["data"][repetition_folder] = {}

            diagram_rep_folder = os.path.join(diagram_folder, repetition_folder)
            os.makedirs(diagram_rep_folder, exist_ok=True)

            for n in config["n_nodes"]:
                self.data[key]["data"][repetition_folder][f"{n:02d}nodes"] = {}
                run_node_path = f"{repetition_path}/{n:02d}nodes"

                # read data into data dictionary
                self.read_run_nodes_data(run_node_path, config,
                        self.data[key]["data"][repetition_folder][f"{n:02d}nodes"])

                # plot cle time profile for every individual node run
                diagram_node_run_folder = os.path.join(diagram_rep_folder, f"{n:02d}nodes")
                os.makedirs(diagram_node_run_folder, exist_ok=True)

                #self.plot_run_node_cle_time_profiler(self.data[key]["data"][repetition_folder][f"{n:02d}nodes"],
                #        diagram_node_run_folder)

            # plot cle time profile for all nodes in run
            #self.plot_run_cle_time_profiler(self.data[key]["data"][repetition_folder],
            #        diagram_rep_folder)

            # plot total time for all nodes in run
            self.plot_total_runtime(config, self.data[key]["data"][repetition_folder],
                                    diagram_rep_folder)

            self.plot_metadata(config, self.data[key]["data"][repetition_folder],
                                    diagram_rep_folder)

            #self.get_linear_expectation(self.data[key]["data"][repetition_folder])

        pprint(self.data)

    def read_yaml_file(self, fname):
        """
        Reads the contents of a yaml file
        """
        with open(fname, 'r') as config_file:
            return yaml.safe_load(config_file)

    def read_run_nodes_data(self, run_node_path, config, data_run_node):
        """
        Reads all data from files of a single run with fixed node number
        :param repetition_path: Folder path to repetition data
        :param config: Configuration parameter for all runs in this data folder
        :param data_run_node: data dictionary to be filled with collected data
        """

        # read metadata
        if config['testcase'] in ['hpcbench_notf', 'hpcbench_readspikes', 'robobrain']:
            metadata = self.read_yaml_file(f"{run_node_path}/metadata.yaml")
            data_run_node["metadata"] = metadata

        # read total time
        with open(f"{run_node_path}/total_time.dat", "r") as datafile:
            data_run_node["runtime"] = float(datafile.read())

        # read cle time profile
        df = pd.read_csv(f"{run_node_path}/cle_time_profile_0.csv")
        data_run_node["cle_time_profile"] = df



    def plot_run_node_cle_time_profiler(self, data_run_node, folder):
        """
        Plots the cle time profile for individual node runs
        :param data_run_node: data for this run and node number
        :param folder: folder path to save figure in
        """
        cle_time_profile = data_run_node['cle_time_profile']

        fig_all_one, ax_all_one = plt.subplots(figsize=figsize)
        fig_all_multi, ax_all_multi = plt.subplots(4, figsize=figsize)

        for i, column in enumerate(cle_profiler_columns):
            fig_single, ax_single = plt.subplots()

            title = f"CLE time profile"
            subtitle = f"{column}"
            fig_single.suptitle(f'{title}')
            ax_single.set_title(f'{subtitle}')
            fig_single.canvas.manager.set_window_title(f'{title} - {subtitle}')
            #ax_single.setp(plt.legend().get_texts(), color='#666')
            ax_single.set_xlabel('cle step', color='#666')
            ax_single.set_ylabel('time (s)', color='#666')
            ax_single.grid(True, axis='y')
            fig_single.tight_layout(pad=0.25, w_pad=0.25, h_pad=0.25)

            ax_single.plot(cle_time_profile.index, cle_time_profile[column], label=column)
            fig_single.savefig(f'{folder}/cle_time_profile-{column}.jpg')

            ax_all_one.plot(cle_time_profile.index, cle_time_profile[column], label=column)

            ax_all_multi[i].plot(cle_time_profile.index, cle_time_profile[column], label=column)
            ax_all_multi[i].set_title(f'{subtitle}')
            ax_all_multi[i].set_xlabel('cle step', color='#666')
            ax_all_multi[i].set_ylabel('time (s)', color='#666')
            ax_all_multi[i].grid(True, axis='y')


        title = f"CLE time profile one"
        #fig_all_one.set_title(f'{title}')
        fig_all_one.suptitle(f'{title}')
        fig_all_one.canvas.manager.set_window_title(f'{title} - all')
        #fig_all.setp(plt.legend().get_texts(), color='#666')
        ax_all_one.set_xlabel('cle step', color='#666')
        ax_all_one.set_ylabel('time (s)', color='#666')
        ax_all_one.grid(True, axis='y')
        fig_all_one.tight_layout(pad=0.25, w_pad=0.25, h_pad=0.25)
        fig_all_one.savefig(f'{folder}/cle_time_profile-all-one.jpg')

        title = f"CLE time profile multi"
        #fig_all_multi.set_title(f'{title}')
        fig_all_multi.suptitle(f'{title}')
        fig_all_multi.canvas.manager.set_window_title(f'{title} - all')
        #fig_all.setp(plt.legend().get_texts(), color='#666')
        fig_all_multi.tight_layout(pad=0.25, w_pad=0.25, h_pad=0.25)
        fig_all_multi.savefig(f'{folder}/cle_time_profile-all-multi.jpg')

        plt.close('all')
        #plt.show()

    def plot_run_cle_time_profiler(self, data_run, folder):
        """
        Plots the cle time profile for all node runs
        :param data_run: data for this run
        :param folder: folder path to save figure in
        """

        for column in cle_profiler_columns:

            fig_column_one, ax_column_one = plt.subplots(figsize=figsize)
            fig_column_multi, ax_column_multi = plt.subplots(len(data_run), figsize=figsize)


            for i, node in enumerate(data_run):
                cle_time_profile = data_run[node]['cle_time_profile']

                title = f"CLE time profile"
                subtitle = f"{column}"
                fig_column_one.suptitle(f'{title}')
                ax_column_one.set_title(f'{subtitle}')
                fig_column_one.canvas.manager.set_window_title(f'{title} - {subtitle}')
                #ax_single.setp(plt.legend().get_texts(), color='#666')
                ax_column_one.set_xlabel('cle step', color='#666')
                ax_column_one.set_ylabel('time (s)', color='#666')
                ax_column_one.grid(True, axis='y')
                fig_column_one.tight_layout(pad=0.25, w_pad=0.25, h_pad=0.25)

                ax_column_one.plot(cle_time_profile.index, cle_time_profile[column], label=column)
                fig_column_one.savefig(f'{folder}/cle_time_profile-{column}-one.jpg')


                ax_column_multi[i].plot(cle_time_profile.index, cle_time_profile[column], label=node)
                ax_column_multi[i].set_xlabel('cle step', color='#666')
                ax_column_multi[i].set_ylabel('time (s)', color='#666')
                ax_column_multi[i].grid(True, axis='y')
                ax_column_multi[i].set_title(node)


            title = f"CLE time profile"
            fig_column_multi.suptitle(f'{title}')
            #ax_column_multi.set_title(f'{subtitle}')
            fig_column_one.canvas.manager.set_window_title(f'{title} - {subtitle}')
            #ax_single.setp(plt.legend().get_texts(), color='#666')
            fig_column_multi.tight_layout(pad=0.25, w_pad=0.25, h_pad=0.25)
            fig_column_multi.savefig(f'{folder}/cle_time_profile-{column}-multi.jpg')

        plt.close('all')



    def get_linear_expectation(self, config, max):
        factors = [n/config["n_nodes"][0] for n in config["n_nodes"]]
        linear = [max/f for f in factors]
        return linear


    def plot_total_runtime(self, config, data_run, folder):
        """
        Plots the total runtime for all nodes in a run
        :param config: Configuration for this run
        :param data_run: data for this run
        :param folder: folder to save the figure in
        """
        fig_all, ax_all = plt.subplots(figsize=figsize)

        runtimes = [data_run[node]['runtime'] for node in data_run]
        linear = self.get_linear_expectation(config, float(list(data_run.values())[0]['runtime']))

        xticks = set()
        x = config["n_nodes"]
        ax_all.plot(x, runtimes, lw=2, c=f"C{i}", label='runtime')
        ax_all.plot(x, linear, lw=4, c=f"C{i}", alpha=0.25)
        for n in config["n_nodes"]:
            xticks.add(n)
            # TODO: get number of neurons and connections from metadata and use in
            # subtitle

        title = "Runtime"
        fig_all.suptitle(f'{title}')
        fig_all.canvas.manager.set_window_title(f'{title}')
        #fig_all.setp(plt.legend().get_texts(), color='#666')
        ax_all.set_xlabel('number of compute nodes', color='#666')
        ax_all.set_xticks(list(xticks))
        ax_all.set_ylabel('total run time (s)', color='#666')
        ax_all.grid(True, axis='y')
        fig_all.tight_layout(pad=0.25, w_pad=0.25, h_pad=0.25)
        fig_all.savefig(f'{folder}/total_runtime.jpg')

    def plot_metadata(self, config, data_run, folder):
        """
        Plots the total runtime for all nodes in a run
        :param config: Configuration for this run
        :param data_run: data for this run
        :param folder: folder to save the figure in
        """
        for type in ['nest_time_connect', 'nest_time_create', 'nest_time_last_simulate',
                     'sacct_averss', 'sacct_elapsed', 'sacct_maxrss']:

            fig_all, ax_all = plt.subplots(figsize=figsize)

            values = [data_run[node]['metadata'][type] for node in data_run]
            linear = self.get_linear_expectation(config, float(list(data_run.values())[0]['metadata'][type]))

            xticks = set()
            x = config["n_nodes"]
            ax_all.plot(x, values, lw=2, c=f"C{i}", label='runtime')
            ax_all.plot(x, linear, lw=4, c=f"C{i}", alpha=0.25)
            for n in config["n_nodes"]:
                xticks.add(n)
                # TODO: get number of neurons and connections from metadata and use in
                # subtitle

            title = type
            fig_all.suptitle(f'{title}')
            fig_all.canvas.manager.set_window_title(f'{title}')
            #fig_all.setp(plt.legend().get_texts(), color='#666')
            ax_all.set_xlabel('number of compute nodes', color='#666')
            ax_all.set_xticks(list(xticks))
            ax_all.set_ylabel('total run time (s)', color='#666')
            ax_all.grid(True, axis='y')
            fig_all.tight_layout(pad=0.25, w_pad=0.25, h_pad=0.25)
            fig_all.savefig(f'{folder}/{type}.jpg')


    def print_network_creation_time(self):
        pass

    def plot_memory(self):
        pass






if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <datadir1> [<datadir2> ...]")

    data_dirs = sys.argv[1:]
    processor = BenchmarkProcessor()

    for i, data_dir in enumerate(data_dirs):
        # loop for all data dirs

        # process data for every run
        processor.process_data_runs(i, data_dir)


        # plot total run times per run in batch
        #processor.plot_total_runtime()

        # plot total run times per run in batch

        # plot
