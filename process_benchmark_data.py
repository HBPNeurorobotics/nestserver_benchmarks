from matplotlib import pyplot as plt
import ruamel.yaml as yaml
from pprint import pprint
import sys
import os
import logging
import glob
import pandas as pd
import time
import numpy as np
import matplotlib
from operator import add
from matplotlib.patches import Patch
from matplotlib.lines import Line2D

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
plt.rc('grid', color='black', ls='dotted')

cle_profiler_columns = ['robot_step', 'brain_step', 'brain_refresh', 'cle_step', 'transfer_function']

experiment_names = {
    "hpcbench_baseline": "NEST standalone",
    "hpcbench_notf": "NRP+NEST, no TF",
    "hpcbench_readspikes": "NRP+NEST, spike-reading TF",
    "robobrain": "RoboBrain experiment"
}

robobrain_tf_switch_times = [5, 25]



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

            if repetition_folder == 'diagrams':
                continue

            # loop for all repetitions in data dir
            repetition_path = os.path.join(results_folder, repetition_folder)
            self.data[key]["data"][repetition_folder] = {}

            diagram_rep_folder = os.path.join(diagram_folder, repetition_folder)
            os.makedirs(diagram_rep_folder, exist_ok=True)

            for n in config["n_tasks"]:
                self.data[key]["data"][repetition_folder][f"{n:02d}_ntasks"] = {}
                run_ntasks_path = f"{repetition_path}/{n:02d}_ntasks"

                # read data into data dictionary
                self.read_run_ntasks_data(run_ntasks_path, config,
                        self.data[key]["data"][repetition_folder][f"{n:02d}_ntasks"])

            # plot cle time profile for all ntasks in run
            self.plot_run_cle_time_profiler(self.data[key]["data"][repetition_folder],
                     diagram_rep_folder)

        # plot total time for all ntasks in repetition
        self.plot_repetition_total_runtime(config, self.data[key]["data"],
                             diagram_folder)

        # plot brain to robot ratio for all  ttasks in repetition
        self.plot_repetition_braintorobot_ratio(config, self.data[key]["data"],
                                diagram_folder)

        # plot total time for all ntasks in repetition
        self.plot_repetition_realtime_factor(config, self.data[key]["data"],
                                diagram_folder)


        # plot metadata for all ntasks in repetition
        self.plot_repetition_metadata(config, self.data[key]["data"],
                             diagram_folder)

        # plot nodehours for all ntasks in repetition
        self.plot_repetition_nodehours(config, self.data[key]["data"],
                              diagram_folder)

        pprint(self.data)

    def read_yaml_file(self, fname):
        """
        Reads the contents of a yaml file
        """
        with open(fname, 'r') as config_file:
            return yaml.safe_load(config_file)

    def remove_outliers(self, data):
        """
        Helper function to remove outliers from a list
        """
        mean = sum(data)/len(data)
        data_cleaned = [x for x in data if abs(mean-x)/mean < 0.12]

        return data_cleaned

    def read_run_ntasks_data(self, run_ntasks_path, config, data_run_ntasks):
        """
        Reads all data from files of a single run with fixed NEST task number
        :param run_ntasks_path: Folder path to ntasks data
        :param config: Configuration parameter for all runs in this data folder
        :param data_run_ntasks: data dictionary to be filled with collected data
        """

        # read metadata
        if config['testcase'] in ['hpcbench_notf', 'hpcbench_readspikes', 'robobrain']:
            metadata = self.read_yaml_file(f"{run_ntasks_path}/metadata.yaml")
            data_run_ntasks["metadata"] = metadata

        # read total time
        with open(f"{run_ntasks_path}/total_time.dat", "r") as datafile:
            data_run_ntasks["runtime"] = float(datafile.read())

        # read cle time profile
        df = pd.read_csv(f"{run_ntasks_path}/cle_time_profile_0.csv")
        data_run_ntasks["cle_time_profile"] = df


    def plot_run_cle_time_profiler(self, data_run, folder):
        """
        Plots the cle time profile for all ntasks runs
        :param data_run: data for this run
        :param folder: folder path to save figure in
        """

        for column in cle_profiler_columns:

            fig_column_one, ax_column_one = plt.subplots(figsize=figsize)

            max_time_list = []
            min_time_list = []
            first_time_list = []

            for i, ntasks in enumerate(data_run):
                cle_time_profile = data_run[ntasks]['cle_time_profile']

                if column=='transfer_function':
                    data = [a - b for a, b in
                            zip(cle_time_profile['cle_step'],
                                list(map(max, zip(cle_time_profile['brain_refresh'] , cle_time_profile['robot_step']))))]
                else:
                    data = cle_time_profile[column]

                max_time_list.append(max(data[1:]))
                first_time_list.append(data[0])
                min_time_list.append(max(data[1:]))

                ax_column_one.plot(cle_time_profile.index, data, label=f"{ntasks[0:2]} NEST proc.", linewidth=6.0)

            bottom, top = ax_column_one.get_ylim()
            if max(max_time_list) > max(first_time_list):
                top = max(max_time_list)
            else:
                top = min(max(max_time_list) * 1.6, max(first_time_list))

            ax_column_one.set_ylim(bottom=max(bottom, 0), top=top)

            title = f"CLE time profile"
            subtitle = f"{column}"
            fig_column_one.suptitle(f'{title}', fontsize=30)
            ax_column_one.set_title(f'{subtitle}', fontsize=25, pad=10)
            fig_column_one.canvas.manager.set_window_title(f'{title} - {subtitle}')
            ax_column_one.set_xlabel('cle step', color='#666', fontsize=22)
            ax_column_one.set_ylabel('time (s)', color='#666', fontsize=22)
            ax_column_one.tick_params(axis='both', which='major', labelsize=18)
            if robobrain_exp:
                for xc in robobrain_tf_switch_times:
                    ax_column_one.axvline(x=xc, color='black', linestyle='--')
            ax_column_one.grid(True, axis='y')
            fig_column_one.tight_layout(pad=0.6, w_pad=0.25, h_pad=0.25)

            if column=='transfer_function':
                ax_column_one.legend(loc="upper right", fontsize=18)
                ax_column_one.set_ylim(bottom=0.00005) # hpc_benchmark
                ax_column_one.set_ylim(bottom=0.035) # robobrain

            fig_column_one.savefig(f'{folder}/cle_time_profile-{column}.svg')

        plt.close('all')


    def get_linear_expectation(self, config, max):
        factors = [n/config["n_tasks"][0] for n in config["n_tasks"]]
        linear = [max/f for f in factors]
        return linear

    def get_linear_expectation_inv(self, config, min):
        factors = [n/config["n_tasks"][0] for n in config["n_tasks"]]
        linear = [min*f for f in factors]
        return linear

    def plot_repetition_total_runtime(self, config, data, folder):
        """
        Plots the total runtime for all ntasks in a all repetitions
        :param config: Configuration for this run
        :param data: data for all repetitions
        :param folder: folder to save the figure in
        """
        fig_all_one, ax_all_one = plt.subplots(figsize=figsize)

        first_values = []
        ax_colors = []
        for rep in range(1, config['repetitions']+1, 1):
            runtimes = [data[f"{rep}"][ntasks]['runtime'] for ntasks in data[f"{rep}"]]
            first_values.append(float(list(data[f"{rep}"].values())[0]['runtime']))

            xticks = set()
            x = config["n_tasks"]
            for n in config["n_tasks"]:
                xticks.add(n)

            ax_plot, = ax_all_one.plot(x, runtimes, c=f"C{rep}", label=f"run{rep}", linewidth=6.0)
            ax_colors.append(ax_plot.get_color())

        first_values_cleaned = self.remove_outliers(first_values)
        linear = self.get_linear_expectation(config, sum(first_values_cleaned)/len(first_values_cleaned))

        ax_all_one.plot(x, linear, c=f"black", alpha=0.25, label='linear', linewidth=8.0)


        patches = []
        for color in ax_colors:
            patches.append(Patch(facecolor=color, edgecolor='black'))
        for i in [1, 3, 5, 7, 9, 11, 13]:
            patches.insert(i, Patch(facecolor='white', edgecolor='white'))
        patches.insert(15, Line2D([0], [0], color=f"black", alpha=0.25, lw=4))
        leg = ax_all_one.legend(handles=patches,
                          labels=14*[''] + ['runs 1-8', 'linear'],
                          ncol=8, handletextpad=0.5, handlelength=1.0, columnspacing=-0.17,
                          loc="upper right", fontsize=18)
        leg._legend_box.align = "left"

        for n in config["n_tasks"]:
            xticks.add(n)

        title = "Runtime"
        fig_all_one.suptitle(f'{title}', fontsize=30)
        fig_all_one.canvas.manager.set_window_title(f'{title}')
        ax_all_one.set_xlabel('number of NEST processes', color='#666', fontsize=22)
        ax_all_one.set_xscale('log')
        ax_all_one.get_xaxis().set_major_formatter(matplotlib.ticker.ScalarFormatter())
        ax_all_one.set_xticks(list(xticks))
        ax_all_one.set_ylabel('time (s)', color='#666', fontsize=22)
        ax_all_one.grid(True, axis='y')
        ax_all_one.tick_params(axis='both', which='major', labelsize=18)
        fig_all_one.tight_layout(pad=0.6, w_pad=0.25, h_pad=0.25)
        fig_all_one.savefig(f'{folder}/total_runtime.svg')

        plt.close('all')

    def plot_repetition_braintorobot_ratio(self, config, data, folder):
        """
        Plots the brain to robot ratio for all ntasks runs
        :param data_run: data for this run
        :param folder: folder path to save figure in
        """

        fig_all, ax_all = plt.subplots(figsize=figsize)

        robot_times = [[data[f"{rep}"][ntasks]['cle_time_profile']['robot_step'][1:].mean()
                        for rep in range(1, config['repetitions']+1, 1)] for ntasks in data[f"1"]]
        brain_times = [[data[f"{rep}"][ntasks]['cle_time_profile']['brain_refresh'][1:].mean()
                         for rep in range(1, config['repetitions']+1, 1)] for ntasks in data[f"1"]]

        robot_means = [sum(x)/len(x) for x in robot_times]
        brain_means = [sum(x)/len(x) for x in brain_times]

        runs = len(robot_times)

        robot_percent = []
        brain_percent = []
        for i in range(len(robot_times)):
            sum_times = robot_means[i] + brain_means[i]
            robot_percent.append(100 * (robot_means[i] / sum_times))
            brain_percent.append(100 * (brain_means[i] / sum_times))

        x = config['n_tasks']
        xticks = set()

        for n in config["n_tasks"]:
            xticks.add(n)

        ax_all.set_xscale('log')
        ax_all.get_xaxis().set_major_formatter(matplotlib.ticker.ScalarFormatter())

        c = 0.2
        ax_all.bar(x, robot_percent, width=c*np.array(x), bottom=brain_percent, color='black')
        ax_all.bar(x, brain_percent, width=c*np.array(x), color='red')

        ax_all.axhline(y=50, color='black', linestyle='--')

        if hpc_exp:
            ax_all.legend(labels=['optimal split', 'robot', 'brain'],
                          loc="lower right", fontsize=18)

        title = "Brain to Robot Ratio"
        fig_all.suptitle(f'{title}', fontsize=25)
        fig_all.canvas.manager.set_window_title(f'{title}')
        ax_all.set_xlabel('number of NEST processes', color='#666', fontsize=22)
        ax_all.set_xticks(list(xticks))
        ax_all.get_xaxis().set_major_formatter(matplotlib.ticker.ScalarFormatter())
        ax_all.set_ylabel('percentage (%)', color='#666', fontsize=22)
        ax_all.grid(True, axis='y')
        ax_all.tick_params(axis='both', which='major', labelsize=18)
        fig_all.tight_layout(pad=0.6, w_pad=0.25, h_pad=0.25)
        fig_all.savefig(f'{folder}/braintorobot_ratio.svg')

        plt.close('all')

    def plot_repetition_realtime_factor(self, config, data, folder):
        """
        Plots the realtime factor for all ntasks in a repetition
        :param config: Configuration for this run
        :param data: data for all repetitions
        :param folder: folder to save the figure in
        """
        fig_all_one, ax_all_one = plt.subplots(figsize=figsize)

        first_values = []
        for rep in range(1, config['repetitions']+1, 1):

            real_time_factors = [0.02 / data[f"{rep}"][ntasks]['cle_time_profile']['cle_step'][1:].mean() for ntasks in data[f"{rep}"]]
            first_values.append(real_time_factors[0])

            xticks = set()
            x = config["n_tasks"]
            for n in config["n_tasks"]:
                xticks.add(n)

            ax_all_one.plot(x, real_time_factors, c=f"C{rep}", label=f"run{rep}", linewidth=6.0)

        first_values_cleaned = self.remove_outliers(first_values)
        linear = self.get_linear_expectation_inv(config, sum(first_values_cleaned)/len(first_values_cleaned))
        ax_plot, =  ax_all_one.plot(x, linear, c=f"black", alpha=0.25, label='linear', linewidth=8.0)
        for n in config["n_tasks"]:
            xticks.add(n)

        title = "Realtime Factor"
        fig_all_one.suptitle(f'{title}', fontsize=30)
        fig_all_one.canvas.manager.set_window_title(f'{title}')
        ax_all_one.set_xlabel('number of NEST processes', color='#666', fontsize=22)
        ax_all_one.set_xscale('log')
        ax_all_one.get_xaxis().set_major_formatter(matplotlib.ticker.ScalarFormatter())
        ax_all_one.set_xticks(list(xticks))
        ax_all_one.set_ylabel('factor sim/real', color='#666', fontsize=22)
        ax_all_one.grid(True, axis='y')
        ax_all_one.tick_params(axis='both', which='major', labelsize=18)
        fig_all_one.tight_layout(pad=0.6, w_pad=0.25, h_pad=0.25)
        fig_all_one.savefig(f'{folder}/realtime_factors.svg')

        plt.close('all')

    def plot_repetition_metadata(self, config, data, folder):
        """
        Plots the total runtime for all ntasks in a repetition
        :param config: Configuration for this run
        :param data: data for all repetitions
        :param folder: folder to save the figure in
        """

        for type in ['nest_time_build', 'nest_time_connect', 'nest_time_create', 'nest_time_last_simulate',
                     'sacct_averss', 'sacct_elapsed', 'sacct_maxrss', 'sacct_consumedenergy']:

            fig_all_one, ax_all_one = plt.subplots(figsize=figsize)

            first_values = []
            ax_colors = []
            for rep in range(1, config['repetitions']+1, 1):

                    if type == 'nest_time_build':
                        values = [data[f"{rep}"][ntasks]['metadata']['nest_time_create']
                                  + data[f"{rep}"][ntasks]['metadata']['nest_time_connect']
                                  for ntasks in data[f"{rep}"]]
                    else:
                        values = [data[f"{rep}"][ntasks]['metadata'][type] for ntasks in data[f"{rep}"]]

                    if type in ['sacct_averss', 'sacct_maxrss']:
                        values = [x / 1000000 for x in values]

                    if type == 'sacct_consumedenergy':
                        values[-1] = values[-1] * 1000

                    if type == 'nest_time_build':
                        first_data = float(list(data[f"{rep}"].values())[0]['metadata']['nest_time_create']) \
                                           + float(list(data[f"{rep}"].values())[0]['metadata']['nest_time_connect'])
                    elif type in ['sacct_averss', 'sacct_maxrss']:
                        first_data = float(list(data[f"{rep}"].values())[0]['metadata'][type]) / 1000000
                    else:
                        first_data = float(list(data[f"{rep}"].values())[0]['metadata'][type])

                    first_values.append(first_data)

                    xticks = set()
                    x = config["n_tasks"]

                    for n in config["n_tasks"]:
                        xticks.add(n)

                    ax_plot, = ax_all_one.plot(x, values, c=f"C{rep}", label=f"run{rep}", linewidth=6.0)
                    ax_colors.append(ax_plot.get_color())

            first_values_cleaned = self.remove_outliers(first_values)
            linear = self.get_linear_expectation(config, sum(first_values_cleaned)/len(first_values_cleaned))
            linear_inv = self.get_linear_expectation_inv(config, sum(first_values_cleaned)/len(first_values_cleaned))

            if type in ['sacct_consumedenergy']:
                lin, = ax_all_one.plot(x, linear_inv, c=f"black", alpha=0.25, label='linear', linewidth=8.0)
            else:
                lin, = ax_all_one.plot(x, linear, c=f"black", alpha=0.25, label='linear', linewidth=8.0)

            if type in ['nest_time_build']:
                patches = []
                for color in ax_colors:
                    patches.append(Patch(facecolor=color, edgecolor='black'))
                for i in [1, 3, 5, 7, 9, 11, 13]:
                    patches.insert(i, Patch(facecolor='white', edgecolor='white'))
                patches.insert(15, Line2D([0], [0], color=f"black", alpha=0.25, lw=4))
                leg = ax_all_one.legend(handles=patches,
                                  labels=14*[''] + ['runs 1-8', 'linear'],
                                  ncol=8, handletextpad=0.5, handlelength=1.0, columnspacing=-0.17,
                                  loc="upper right", fontsize=18)
                leg._legend_box.align = "left"

            for n in config["n_tasks"]:
                xticks.add(n)

            title = type
            fig_all_one.suptitle(f'{title}', fontsize=30)

            if title is 'nest_time_build':
                fig_title = 'NEST network building time'
            elif title is 'nest_time_connect':
                fig_title = 'NEST network connection time'
            elif title is 'nest_time_create':
                fig_title = 'NEST network creation time'
            elif title is 'nest_time_last_simulate':
                fig_title = 'NEST time of last simulation step'
            elif title is 'sacct_averss':
                fig_title = 'Job average resident set size'
            elif title is 'sacct_elapsed':
                fig_title = 'Job elapsed time'
            elif title is 'sacct_maxrss':
                fig_title = 'Job maximum resident set size'
            elif title is 'sacct_consumedenergy':
                fig_title = 'Job total consumed energy'

            fig_all_one.suptitle(fig_title, fontsize=30)

            fig_all_one.canvas.manager.set_window_title(f'{title}')
            ax_all_one.set_xlabel('number of NEST processes', color='#666', fontsize=22)
            ax_all_one.set_xscale('log')
            ax_all_one.get_xaxis().set_major_formatter(matplotlib.ticker.ScalarFormatter())
            ax_all_one.set_xticks(list(xticks))
            ax_all_one.set_ylabel('time (s)', color='#666', fontsize=22)
            if type in ['sacct_averss', 'sacct_maxrss']:
                ax_all_one.set_ylabel('RAM (GB)', color='#666')
            if type in ['sacct_consumedenergy']:
                ax_all_one.set_ylabel('energy (kJ)', color='#666')

            ax_all_one.grid(True, axis='y')
            ax_all_one.tick_params(axis='both', which='major', labelsize=18)
            fig_all_one.tight_layout(pad=0.6, w_pad=0.25, h_pad=0.25)
            fig_all_one.savefig(f'{folder}/{type}.svg')

            plt.close('all')


    def plot_repetition_nodehours(self, config, data, folder):
        """
        Plots the nodehours used for all ntasks in a repetition
        :param config: Configuration for this run
        :param data: data for this run
        :param folder: folder to save the figure in
        """
        fig_all, ax_all = plt.subplots(figsize=figsize)

        first_values = []
        ax_colors = []
        for rep in range(1, config['repetitions']+1, 1):

            runtimes = [data[f"{rep}"][ntasks]['runtime']/3600 for ntasks in data[f"{rep}"]]
            ntasks = [int(ntasks.replace("_ntasks", "")) for ntasks in data[f"{rep}"]]
            nodehours = [a * b for a, b in zip(ntasks, runtimes)]
            first_values.append(nodehours[0])

            xticks = set()
            x = config["n_tasks"]
            ax_plot, = ax_all.plot(x, nodehours, c=f"C{rep}", label=f"run{rep}", linewidth=6.0)
            ax_colors.append(ax_plot.get_color())

        first_values_cleaned = self.remove_outliers(first_values)
        linear = self.get_linear_expectation_inv(config, sum(first_values_cleaned)/len(first_values_cleaned))
        ax_all.plot(x, linear, c=f"black", alpha=0.25, label='linear', linewidth=8.0)

        patches = []
        for color in ax_colors:
            patches.append(Patch(facecolor=color, edgecolor='black'))
        for i in [1, 3, 5, 7, 9, 11, 13]:
            patches.insert(i, Patch(facecolor='white', edgecolor='white'))
        patches.insert(15, Line2D([0], [0], color=f"black", alpha=0.25, lw=4))
        if hpc_exp:
            leg = ax_all.legend(handles=patches,
                              labels=14*[''] + ['runs 1-8', 'linear'],
                              ncol=8, handletextpad=0.5, handlelength=1.0, columnspacing=-0.17,
                              loc="upper left", fontsize=18)
            leg._legend_box.align = "left"

        for n in config["n_tasks"]:
            xticks.add(n)

        title = "Node Hours"
        fig_all.suptitle(f'{title}', fontsize=25)
        fig_all.canvas.manager.set_window_title(f'{title}')
        ax_all.set_xlabel('number of NEST processes', color='#666', fontsize=22)
        ax_all.set_xscale('log')
        ax_all.get_xaxis().set_major_formatter(matplotlib.ticker.ScalarFormatter())
        ax_all.set_xticks(list(xticks))
        ax_all.set_ylabel('node hours (h)', color='#666', fontsize=22)
        ax_all.grid(True, axis='y')
        ax_all.tick_params(axis='both', which='major', labelsize=18)
        fig_all.tight_layout(pad=0.6, w_pad=0.25, h_pad=0.25)

        fig_all.savefig(f'{folder}/nodehours.svg')


        plt.close('all')


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <datadir1> [<datadir2> ...]")

    data_dirs = sys.argv[1:]

    robobrain_exp = False
    hpc_exp = False
    for dir in data_dirs:
         if "robobrain" in dir:
             robobrain_exp = True
         if "hpc" in dir:
             hpc_exp = True


    processor = BenchmarkProcessor()

    for i, data_dir in enumerate(data_dirs):
        # loop for all data dirs and process data for every run
        processor.process_data_runs(i, data_dir)
