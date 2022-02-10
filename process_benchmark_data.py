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

cle_profiler_columns = ['robot_step', 'brain_step', 'brain_refresh', 'cle_step', 'transfer_function']

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

                # plot cle time profile for every individual ntasks run
                diagram_ntasks_run_folder = os.path.join(diagram_rep_folder, f"{n:02d}_ntasks")
                os.makedirs(diagram_ntasks_run_folder, exist_ok=True)

                # self.plot_run_ntasks_cle_time_profiler(self.data[key]["data"][repetition_folder][f"{n:02d}_ntasks"],
                #          diagram_ntasks_run_folder, n)

            # plot cle time profile for all ntasks in run
            self.plot_run_cle_time_profiler(self.data[key]["data"][repetition_folder],
                     diagram_rep_folder)

            # plot realtime factor for all ntasks in run
            self.plot_run_realtime_factor(config, self.data[key]["data"][repetition_folder],
                     diagram_rep_folder)

            # plot brain to robot ratio for all ntasks in run
            self.plot_run_braintorobot_ratio(config, self.data[key]["data"][repetition_folder],
                 diagram_rep_folder)

            # plot total time for all ntasks in run
            self.plot_run_total_runtime(config, self.data[key]["data"][repetition_folder],
                                 diagram_rep_folder)

            # plot nodehours for all ntasks in run
            self.plot_run_nodehours(config, self.data[key]["data"][repetition_folder],
                                             diagram_rep_folder)

            # plot metadta for all ntasks in run
            self.plot_run_metadata(config, self.data[key]["data"][repetition_folder],
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

        # plot metadta for all ntasks in run
        self.plot_run_metadata(config, self.data[key]["data"][repetition_folder],
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



    def plot_run_ntasks_cle_time_profiler(self, data_run_ntasks, folder, ntasks):
        """
        Plots the cle time profile for individual ntasks runs
        :param data_run_ntasks: data for this run and ntasks number
        :param folder: folder path to save figure in
        :param ntasks: number of tasks in this run
        """
        cle_time_profile = data_run_ntasks['cle_time_profile']

        fig_all_one, ax_all_one = plt.subplots(figsize=figsize)
        fig_all_multi, ax_all_multi = plt.subplots(5, figsize=figsize)
        fig_all_one_second, ax_all_one_second = plt.subplots(figsize=figsize)

        for i, column in enumerate(cle_profiler_columns):
            fig_single, ax_single = plt.subplots()

            title = f"CLE time profile - {ntasks} NEST processes"
            subtitle = f"{column}"
            fig_single.suptitle(f'{title}', fontsize=18)
            ax_single.set_title(f'{subtitle}', fontsize=14, pad=10)
            fig_single.canvas.manager.set_window_title(f'{title} - {subtitle}')
            #ax_single.setp(plt.legend().get_texts(), color='#666')
            ax_single.set_xlabel('cle step', color='#666')
            ax_single.set_ylabel('time (s)', color='#666')
            ax_single.grid(True, axis='y')
            fig_single.tight_layout(pad=0.6, w_pad=0.25, h_pad=0.25)

            if column=='transfer_function':
                # Todo: Only true if brain takes longer than robot step
                data = [a - b for a, b in zip(cle_time_profile['cle_step'], cle_time_profile['brain_refresh'])]
            else:
                data = cle_time_profile[column]

            ax_single.plot(cle_time_profile.index, data, label=column)
            ax_single.legend(loc="upper right")
            fig_single.savefig(f'{folder}/cle_time_profile-{column}.jpg')

            ax_all_one.plot(cle_time_profile.index, data, label=column)
            ax_all_one_second.plot(cle_time_profile.index[1:], data[1:], label=column)

            ax_all_multi[i].plot(cle_time_profile.index, data, label=column)
            ax_all_multi[i].set_title(f'{subtitle}', fontsize=16, pad=10)
            ax_all_multi[i].set_xlabel('cle step', color='#666')
            ax_all_multi[i].set_ylabel('time (s)', color='#666')
            ax_all_multi[i].grid(True, axis='y')
            ax_all_multi[i].legend(loc="upper right")


        title = f"CLE time profile ({ntasks} NEST processes)"
        #fig_all_one.set_title(f'{title}')
        fig_all_one.suptitle(f'{title}', fontsize=20)
        fig_all_one.canvas.manager.set_window_title(f'{title} - all')
        #fig_all.setp(plt.legend().get_texts(), color='#666')
        ax_all_one.set_xlabel('cle step', color='#666')
        ax_all_one.set_ylabel('time (s)', color='#666')
        ax_all_one.grid(True, axis='y')
        ax_all_one.legend(loc="upper right")
        fig_all_one.tight_layout(pad=0.6, w_pad=0.25, h_pad=0.25)
        fig_all_one.savefig(f'{folder}/cle_time_profile-all-one.jpg')

        title = f"CLE time profile without first step ({ntasks} NEST processes)"
        #fig_all_one.set_title(f'{title}')
        fig_all_one_second.suptitle(f'{title}', fontsize=20)
        fig_all_one_second.canvas.manager.set_window_title(f'{title} - all')
        #fig_all.setp(plt.legend().get_texts(), color='#666')
        ax_all_one_second.set_xlabel('cle step', color='#666')
        ax_all_one_second.set_ylabel('time (s)', color='#666')
        ax_all_one_second.grid(True, axis='y')
        ax_all_one_second.legend(loc="upper right")
        fig_all_one_second.tight_layout(pad=0.6, w_pad=0.25, h_pad=0.25)
        fig_all_one_second.savefig(f'{folder}/cle_time_profile-all-one-second.jpg')

        title = f"CLE time profile multi - {ntasks} NEST processes"
        #fig_all_multi.set_title(f'{title}')
        fig_all_multi.suptitle(f'{title}', fontsize=20)
        fig_all_multi.canvas.manager.set_window_title(f'{title} - all')
        #fig_all.setp(plt.legend().get_texts(), color='#666')
        fig_all_multi.tight_layout(pad=0.6, w_pad=0.25, h_pad=0.25)
        fig_all_multi.savefig(f'{folder}/cle_time_profile-all-multi.jpg')

        plt.close('all')
        #plt.show()

    def plot_run_cle_time_profiler(self, data_run, folder):
        """
        Plots the cle time profile for all ntasks runs
        :param data_run: data for this run
        :param folder: folder path to save figure in
        """

        for column in cle_profiler_columns:

            fig_column_one, ax_column_one = plt.subplots(figsize=figsize)
            fig_column_one_second, ax_column_one_second = plt.subplots(figsize=figsize)
            fig_column_multi, ax_column_multi = plt.subplots(len(data_run), figsize=figsize)

            for i, ntasks in enumerate(data_run):
                cle_time_profile = data_run[ntasks]['cle_time_profile']

                if column=='transfer_function':
                    # Todo: Only true if brain takes longer than robot step
                    data = [a - b for a, b in zip(cle_time_profile['cle_step'], cle_time_profile['brain_refresh'])]
                else:
                    data = cle_time_profile[column]

                ax_column_multi[i].plot(cle_time_profile.index, data, label=ntasks)
                ax_column_multi[i].set_xlabel('cle step', color='#666')
                ax_column_multi[i].set_ylabel('time (s)', color='#666')
                ax_column_multi[i].grid(True, axis='y')
                #ax_column_multi[i].set_title(ntasks)
                ax_column_multi[i].legend(loc="upper right")

                ax_column_one.plot(cle_time_profile.index, data, label=f"{ntasks[0:2]} NEST tasks")
                ax_column_one_second.plot(cle_time_profile.index[1:], data[1:], label=f"{ntasks[0:2]} NEST tasks")


            title = f"CLE time profile"
            subtitle = f"{column}"
            fig_column_one.suptitle(f'{title}', fontsize=20)
            ax_column_one.set_title(f'{subtitle}', fontsize=16, pad=10)
            fig_column_one.canvas.manager.set_window_title(f'{title} - {subtitle}')
            #ax_single.setp(plt.legend().get_texts(), color='#666')
            ax_column_one.set_xlabel('cle step', color='#666')
            ax_column_one.set_ylabel('time (s)', color='#666')
            ax_column_one.grid(True, axis='y')
            fig_column_one.tight_layout(pad=0.6, w_pad=0.25, h_pad=0.25)

            ax_column_one.legend(loc="upper right")
            fig_column_one.savefig(f'{folder}/cle_time_profile-{column}-one.jpg')


            title = f"CLE time profile"
            subtitle = f"{column}"
            fig_column_one_second.suptitle(f'{title}', fontsize=20)
            ax_column_one_second.set_title(f'{subtitle}', fontsize=16, pad=10)
            fig_column_one_second.canvas.manager.set_window_title(f'{title} - {subtitle}')
            #ax_single.setp(plt.legend().get_texts(), color='#666')
            ax_column_one_second.set_xlabel('cle step', color='#666')
            ax_column_one_second.set_ylabel('time (s)', color='#666')
            ax_column_one_second.grid(True, axis='y')
            fig_column_one_second.tight_layout(pad=0.6, w_pad=0.25, h_pad=0.25)

            ax_column_one_second.legend(loc="upper right")
            fig_column_one_second.savefig(f'{folder}/cle_time_profile-{column}-one-second.jpg')

            title = f"CLE time profile - {column}"
            fig_column_multi.suptitle(f'{title}', fontsize=20)
            #ax_column_multi.set_title(f'{subtitle}', fontsize=16, pad=10)
            fig_column_one.canvas.manager.set_window_title(f'{title} - {subtitle}')
            #ax_single.setp(plt.legend().get_texts(), color='#666')
            fig_column_multi.tight_layout(pad=0.6, w_pad=0.25, h_pad=0.25)
            fig_column_multi.savefig(f'{folder}/cle_time_profile-{column}-multi.jpg')

        plt.close('all')


    def plot_run_realtime_factor(self, config, data_run, folder):
        """
        Plots the realtime factor for all ntasks runs
        :param data_run: data for this run
        :param folder: folder path to save figure in
        """

        fig_all, ax_all = plt.subplots(figsize=figsize)

        real_time_factors = [0.02 / data_run[ntasks]['cle_time_profile']['cle_step'][1:].mean() for ntasks in data_run]
        linear_inv = self.get_linear_expectation_inv(config, min(real_time_factors))

        xticks = set()
        x = config["n_tasks"]
        ax_all.plot(x, real_time_factors, lw=2, c=f"C{i}", label='Realtime Factor')
        ax_all.plot(x, linear_inv, lw=4, c=f"C{i}", alpha=0.25, label='linear')
        ax_all.legend(loc="upper right")
        for n in config["n_tasks"]:
            xticks.add(n)
            # TODO: get number of neurons and connections from metadata and use in
            # subtitle

        title = "Realtime Factor"
        fig_all.suptitle(f'{title}', fontsize=20)
        fig_all.canvas.manager.set_window_title(f'{title}')
        #fig_all.setp(plt.legend().get_texts(), color='#666')
        ax_all.set_xlabel('number of NEST processes', color='#666')
        ax_all.set_xscale('log')
        ax_all.get_xaxis().set_major_formatter(matplotlib.ticker.ScalarFormatter())
        ax_all.set_xticks(list(xticks))
        ax_all.set_ylabel('factor sim/real', color='#666')
        ax_all.grid(True, axis='y')
        fig_all.tight_layout(pad=0.6, w_pad=0.25, h_pad=0.25)
        fig_all.savefig(f'{folder}/realtime_factor.jpg')

        plt.close('all')


    def plot_run_braintorobot_ratio(self, config, data_run, folder):
        """
        Plots the brain to robot ratio for all ntasks runs
        :param data_run: data for this run
        :param folder: folder path to save figure in
        """

        fig_all, ax_all = plt.subplots(figsize=figsize)

        robot_times = [data_run[ntasks]['cle_time_profile']['robot_step'][1:].mean() for ntasks in data_run]
        brain_times = [data_run[ntasks]['cle_time_profile']['brain_step'][1:].mean() for ntasks in data_run]
        runs = len(robot_times)

        robot_percent = []
        brain_percent = []
        for i in range(runs):
            sum_times = robot_times[i] + brain_times[i]
            robot_percent.append(100 * (robot_times[i] / sum_times))
            brain_percent.append(100 * (brain_times[i] / sum_times))

        x = config['n_tasks']
        xticks = set()

        for n in config["n_tasks"]:
            xticks.add(n)

        c = 0.2
        ax_all.bar(x, robot_percent, width=c*np.array(x), bottom=brain_percent, color='black')
        ax_all.bar(x, brain_percent, width=c*np.array(x), color='red')

        ax_all.axhline(y=50, color='black', linestyle='--')

        ax_all.legend(labels=['optimal split', 'robot', 'brain'], loc="lower right")

        title = "Brain to Robot Ratio"
        fig_all.suptitle(f'{title}', fontsize=20)
        fig_all.canvas.manager.set_window_title(f'{title}')
        #fig_all.setp(plt.legend().get_texts(), color='#666')
        ax_all.set_xlabel('number of NEST processes', color='#666')
        ax_all.set_xscale('log')
        ax_all.get_xaxis().set_major_formatter(matplotlib.ticker.ScalarFormatter())
        ax_all.set_xticks(list(xticks))
        ax_all.set_ylabel('percentage (%)', color='#666')
        ax_all.grid(True, axis='y')
        fig_all.tight_layout(pad=0.6, w_pad=0.25, h_pad=0.25)
        fig_all.savefig(f'{folder}/braintorobot_ratio.jpg')

        plt.close('all')



    def get_linear_expectation(self, config, max):
        factors = [n/config["n_tasks"][0] for n in config["n_tasks"]]
        linear = [max/f for f in factors]
        return linear

    def get_linear_expectation_inv(self, config, min):
        factors = [n/config["n_tasks"][0] for n in config["n_tasks"]]
        linear = [min*f for f in factors]
        return linear

    def plot_run_total_runtime(self, config, data_run, folder):
        """
        Plots the total runtime for all ntasks in a run
        :param config: Configuration for this run
        :param data_run: data for this run
        :param folder: folder to save the figure in
        """
        fig_all, ax_all = plt.subplots(figsize=figsize)

        runtimes = [data_run[ntasks]['runtime'] for ntasks in data_run]
        linear = self.get_linear_expectation(config, float(list(data_run.values())[0]['runtime']))

        xticks = set()
        x = config["n_tasks"]
        ax_all.plot(x, runtimes, lw=2, c=f"C{i}", label='runtime')
        ax_all.plot(x, linear, lw=4, c=f"C{i}", alpha=0.25, label='linear')
        ax_all.legend(loc="upper right")
        for n in config["n_tasks"]:
            xticks.add(n)
            # TODO: get number of neurons and connections from metadata and use in
            # subtitle

        title = "Runtime"
        fig_all.suptitle(f'{title}', fontsize=20)
        fig_all.canvas.manager.set_window_title(f'{title}')
        #fig_all.setp(plt.legend().get_texts(), color='#666')
        ax_all.set_xlabel('number of NEST processes', color='#666')
        ax_all.set_xscale('log')
        ax_all.get_xaxis().set_major_formatter(matplotlib.ticker.ScalarFormatter())
        ax_all.set_xticks(list(xticks))
        ax_all.set_ylabel('time (s)', color='#666')
        ax_all.grid(True, axis='y')
        fig_all.tight_layout(pad=0.6, w_pad=0.25, h_pad=0.25)
        fig_all.savefig(f'{folder}/total_runtime.jpg')

        plt.close('all')

    def plot_run_nodehours(self, config, data_run, folder):
        """
        Plots the nodehours used for all ntasks in a run
        :param config: Configuration for this run
        :param data_run: data for this run
        :param folder: folder to save the figure in
        """
        fig_all, ax_all = plt.subplots(figsize=figsize)

        runtimes = [data_run[ntasks]['runtime']/3600 for ntasks in data_run]
        ntasks = [int(ntasks.replace("_ntasks", "")) for ntasks in data_run]
        nodehours = [a * b for a, b in zip(ntasks, runtimes)]

        linear = self.get_linear_expectation_inv(config, nodehours[0]) #float(list(data_run.values())[0]['runtime']))

        xticks = set()
        x = config["n_tasks"]
        ax_all.plot(x, nodehours, lw=2, c=f"C{i}", label='runtime')
        ax_all.plot(x, linear, lw=4, c=f"C{i}", alpha=0.25, label='linear')
        ax_all.legend(loc="upper right")
        for n in config["n_tasks"]:
            xticks.add(n)
            # TODO: get number of neurons and connections from metadata and use in
            # subtitle

        title = "Node Hours"
        fig_all.suptitle(f'{title}', fontsize=20)
        fig_all.canvas.manager.set_window_title(f'{title}')
        #fig_all.setp(plt.legend().get_texts(), color='#666')
        ax_all.set_xlabel('number of NEST processes', color='#666')
        ax_all.set_xscale('log')
        ax_all.get_xaxis().set_major_formatter(matplotlib.ticker.ScalarFormatter())
        ax_all.set_xticks(list(xticks))
        ax_all.set_ylabel('node hours (h)', color='#666')
        ax_all.grid(True, axis='y')
        fig_all.tight_layout(pad=0.6, w_pad=0.25, h_pad=0.25)
        fig_all.savefig(f'{folder}/nodehours.jpg')

        plt.close('all')

    def plot_run_metadata(self, config, data_run, folder):
        """
        Plots the total runtime for all ntasks in a run
        :param config: Configuration for this run
        :param data_run: data for this run
        :param folder: folder to save the figure in
        """
        for type in ['nest_time_connect', 'nest_time_create', 'nest_time_last_simulate',
                     'sacct_averss', 'sacct_elapsed', 'sacct_maxrss', 'sacct_consumedenergy']:

            fig_all, ax_all = plt.subplots(figsize=figsize)

            values = [data_run[ntasks]['metadata'][type] for ntasks in data_run]
            linear = self.get_linear_expectation(config, float(list(data_run.values())[0]['metadata'][type]))
            linear_inv = self.get_linear_expectation_inv(config, float(list(data_run.values())[0]['metadata'][type]))

            xticks = set()
            x = config["n_tasks"]
            ax_all.plot(x, values, lw=2, c=f"C{i}", label='runtime')
            if type in ['sacct_consumedenergy']:
                ax_all.plot(x, linear_inv, lw=4, c=f"C{i}", alpha=0.25, label='linear')
            else:
                ax_all.plot(x, linear, lw=4, c=f"C{i}", alpha=0.25, label='linear')

            ax_all.legend(loc="upper right")

            for n in config["n_tasks"]:
                xticks.add(n)
                # TODO: get number of neurons and connections from metadata and use in
                # subtitle

            title = type
            fig_all.suptitle(f'{title}', fontsize=20)
            fig_all.canvas.manager.set_window_title(f'{title}')
            #fig_all.setp(plt.legend().get_texts(), color='#666')
            ax_all.set_xlabel('number of NEST tasks', color='#666')
            ax_all.set_xscale('log')
            ax_all.get_xaxis().set_major_formatter(matplotlib.ticker.ScalarFormatter())
            ax_all.set_xticks(list(xticks))
            ax_all.set_ylabel('time (s)', color='#666')
            if type in ['sacct_averss', 'sacct_maxrss']:
                ax_all.set_ylabel('RAM (kB)', color='#666')
            if type in ['sacct_consumedenergy']:
                ax_all.set_ylabel('energy (kJ)', color='#666')

            ax_all.grid(True, axis='y')
            fig_all.tight_layout(pad=0.6, w_pad=0.25, h_pad=0.25)
            fig_all.savefig(f'{folder}/{type}.jpg')

        plt.close('all')


    def plot_repetition_total_runtime(self, config, data, folder):
        """
        Plots the total runtime for all ntasks in a all repetitions
        :param config: Configuration for this run
        :param data: data for all repetitions
        :param folder: folder to save the figure in
        """
        fig_all_multi, ax_all_multi = plt.subplots(config['repetitions'], figsize=figsize)
        fig_all_one, ax_all_one = plt.subplots(figsize=figsize)

        first_values = []
        for rep in range(1, config['repetitions']+1, 1):
            runtimes = [data[f"{rep}"][ntasks]['runtime'] for ntasks in data[f"{rep}"]]
            first_values.append(float(list(data[f"{rep}"].values())[0]['runtime']))

            linear_multi = self.get_linear_expectation(config, float(list(data[f"{rep}"].values())[0]['runtime']))

            xticks = set()
            x = config["n_tasks"]
            ax_all_multi[rep-1].plot(x, runtimes, lw=2, c=f"C{i}", label=f"run{rep}")
            ax_all_multi[rep-1].plot(x, linear_multi, lw=4, c=f"C{i}", alpha=0.25, label='linear')
            ax_all_multi[rep-1].legend(loc="upper right")
            for n in config["n_tasks"]:
                xticks.add(n)
                # TODO: get number of neurons and connections from metadata and use in
                # subtitle

            ax_all_multi[rep-1].set_xlabel('number of NEST processes', color='#666')
            ax_all_multi[rep-1].set_xscale('log')
            ax_all_multi[rep-1].get_xaxis().set_major_formatter(matplotlib.ticker.ScalarFormatter())
            ax_all_multi[rep-1].set_xticks(list(xticks))
            ax_all_multi[rep-1].set_ylabel('time (s)', color='#666')
            ax_all_multi[rep-1].grid(True, axis='y')

            ax_all_one.plot(x, runtimes, lw=2, c=f"C{rep}", label=f"run{rep}")

        first_values_cleaned = self.remove_outliers(first_values)
        linear = self.get_linear_expectation(config, sum(first_values_cleaned)/len(first_values_cleaned))

        ax_all_one.plot(x, linear, lw=4, c=f"C{i}", alpha=0.25, label='linear')
        ax_all_one.legend(loc="upper right")
        for n in config["n_tasks"]:
            xticks.add(n)

        title = "Runtime"
        fig_all_one.suptitle(f'{title}', fontsize=20)
        fig_all_one.canvas.manager.set_window_title(f'{title}')
        #fig_all.setp(plt.legend().get_texts(), color='#666')
        ax_all_one.set_xlabel('number of NEST processes', color='#666')
        ax_all_one.set_xscale('log')
        ax_all_one.get_xaxis().set_major_formatter(matplotlib.ticker.ScalarFormatter())
        ax_all_one.set_xticks(list(xticks))
        ax_all_one.set_ylabel('time (s)', color='#666')
        ax_all_one.grid(True, axis='y')
        fig_all_one.tight_layout(pad=0.6, w_pad=0.25, h_pad=0.25)
        fig_all_one.savefig(f'{folder}/total_runtime-one.jpg')


        title = "Runtime"
        fig_all_multi.suptitle(f'{title}', fontsize=20)
        fig_all_multi.canvas.manager.set_window_title(f'{title}')
        fig_all_multi.tight_layout(pad=0.6, w_pad=0.25, h_pad=0.25)
        fig_all_multi.savefig(f'{folder}/total_runtime-multi.jpg')

        plt.close('all')

    def plot_repetition_braintorobot_ratio(self, config, data, folder):
        """
        Plots the brain to robot ratio for all ntasks runs
        :param data_run: data for this run
        :param folder: folder path to save figure in
        """

        fig_all, ax_all = plt.subplots(figsize=figsize)

        robot_times = [[data[f"{rep}"][ntasks]['cle_time_profile']['robot_step'][1:].mean() for rep in range(1, config['repetitions']+1, 1)] for ntasks in data[f"1"]]
        brain_times = [[data[f"{rep}"][ntasks]['cle_time_profile']['brain_step'][1:].mean() for rep in range(1, config['repetitions']+1, 1)] for ntasks in data[f"1"]]

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

        ax_all.legend(labels=['optimal split', 'robot', 'brain'], loc="lower right")

        title = "Brain to Robot Ratio"
        fig_all.suptitle(f'{title}', fontsize=20)
        fig_all.canvas.manager.set_window_title(f'{title}')
        #fig_all.setp(plt.legend().get_texts(), color='#666')
        ax_all.set_xlabel('number of NEST processes', color='#666')
        ax_all.set_xticks(list(xticks))
        ax_all.get_xaxis().set_major_formatter(matplotlib.ticker.ScalarFormatter())
        ax_all.set_ylabel('percentage (%)', color='#666')
        ax_all.grid(True, axis='y')
        fig_all.tight_layout(pad=0.6, w_pad=0.25, h_pad=0.25)
        fig_all.savefig(f'{folder}/braintorobot_ratio.jpg')

        plt.close('all')

    def plot_repetition_realtime_factor(self, config, data, folder):
        """
        Plots the realtime factor for all ntasks in a repetition
        :param config: Configuration for this run
        :param data: data for all repetitions
        :param folder: folder to save the figure in
        """
        fig_all_multi, ax_all_multi = plt.subplots(config['repetitions'], figsize=figsize)
        fig_all_one, ax_all_one = plt.subplots(figsize=figsize)

        first_values = []
        for rep in range(1, config['repetitions']+1, 1):

            real_time_factors = [0.02 / data[f"{rep}"][ntasks]['cle_time_profile']['cle_step'][1:].mean() for ntasks in data[f"{rep}"]]
            first_values.append(real_time_factors[0])
            linear_multi = self.get_linear_expectation_inv(config, real_time_factors[0])

            xticks = set()
            x = config["n_tasks"]
            ax_all_multi[rep-1].plot(x, real_time_factors, lw=2, c=f"C{i}", label=f"run{rep}")
            ax_all_multi[rep-1].plot(x, linear_multi, lw=4, c=f"C{i}", alpha=0.25, label='linear')
            ax_all_multi[rep-1].legend(loc="upper right")
            for n in config["n_tasks"]:
                xticks.add(n)
                # TODO: get number of neurons and connections from metadata and use in
                # subtitle

            ax_all_multi[rep-1].set_xlabel('number of NEST processes', color='#666')
            ax_all_multi[rep-1].set_xscale('log')
            ax_all_multi[rep-1].get_xaxis().set_major_formatter(matplotlib.ticker.ScalarFormatter())
            ax_all_multi[rep-1].set_xticks(list(xticks))
            ax_all_multi[rep-1].set_ylabel('factor sim/real', color='#666')
            ax_all_multi[rep-1].grid(True, axis='y')

            ax_all_one.plot(x, real_time_factors, lw=2, c=f"C{rep}", label=f"run{rep}")

        first_values_cleaned = self.remove_outliers(first_values)
        linear = self.get_linear_expectation_inv(config, sum(first_values_cleaned)/len(first_values_cleaned))
        ax_all_one.plot(x, linear, lw=4, c=f"C{i}", alpha=0.25, label='linear')
        ax_all_one.legend(loc="upper right")
        for n in config["n_tasks"]:
            xticks.add(n)

        title = "Realtime Factor"
        fig_all_one.suptitle(f'{title}', fontsize=20)
        fig_all_one.canvas.manager.set_window_title(f'{title}')
        #fig_all.setp(plt.legend().get_texts(), color='#666')
        ax_all_one.set_xlabel('number of NEST processes', color='#666')
        ax_all_one.set_xscale('log')
        ax_all_one.get_xaxis().set_major_formatter(matplotlib.ticker.ScalarFormatter())
        ax_all_one.set_xticks(list(xticks))
        ax_all_one.set_ylabel('factor sim/real', color='#666')
        ax_all_one.grid(True, axis='y')
        fig_all_one.tight_layout(pad=0.6, w_pad=0.25, h_pad=0.25)
        fig_all_one.savefig(f'{folder}/realtime_factors-one.jpg')

        title = "Realtime Factor"
        fig_all_multi.suptitle(f'{title}', fontsize=20)
        fig_all_multi.canvas.manager.set_window_title(f'{title}')
        fig_all_multi.tight_layout(pad=0.6, w_pad=0.25, h_pad=0.25)
        fig_all_multi.savefig(f'{folder}/realtime_factors-multi.jpg')

        plt.close('all')

    def plot_repetition_metadata(self, config, data, folder):
        """
        Plots the total runtime for all ntasks in a repetition
        :param config: Configuration for this run
        :param data: data for all repetitions
        :param folder: folder to save the figure in
        """

        for type in ['nest_time_connect', 'nest_time_create', 'nest_time_last_simulate',
                     'sacct_averss', 'sacct_elapsed', 'sacct_maxrss', 'sacct_consumedenergy']:

            fig_all_multi, ax_all_multi = plt.subplots(config['repetitions'], figsize=figsize)

            fig_all_one, ax_all_one = plt.subplots(figsize=figsize)

            first_values = []
            for rep in range(1, config['repetitions']+1, 1):

                    values = [data[f"{rep}"][ntasks]['metadata'][type] for ntasks in data[f"{rep}"]]
                    first_values.append(float(list(data[f"{rep}"].values())[0]['metadata'][type]))
                    linear_multi = self.get_linear_expectation(config, float(list(data[f"{rep}"].values())[0]['metadata'][type]))
                    linear_inv_multi = self.get_linear_expectation_inv(config, float(list(data[f"{rep}"].values())[0]['metadata'][type]))

                    xticks = set()
                    x = config["n_tasks"]
                    ax_all_multi[rep-1].plot(x, values, lw=2, c=f"C{i}", label=f"run{rep}")
                    if type in ['sacct_consumedenergy']:
                        ax_all_multi[rep-1].plot(x, linear_inv_multi, lw=4, c=f"C{i}", alpha=0.25, label='linear')
                    else:
                        ax_all_multi[rep-1].plot(x, linear_multi, lw=4, c=f"C{i}", alpha=0.25, label='linear')

                    ax_all_multi[rep-1].legend(loc="upper right")

                    for n in config["n_tasks"]:
                        xticks.add(n)
                        # TODO: get number of neurons and connections from metadata and use in
                        # subtitle


                    ax_all_multi[rep-1].set_xlabel('number of NEST tasks', color='#666')
                    ax_all_multi[rep-1].set_xscale('log')
                    ax_all_multi[rep-1].get_xaxis().set_major_formatter(matplotlib.ticker.ScalarFormatter())
                    ax_all_multi[rep-1].set_xticks(list(xticks))
                    ax_all_multi[rep-1].set_ylabel('time (s)', color='#666')
                    if type in ['sacct_averss', 'sacct_maxrss']:
                        ax_all_multi[rep-1].set_ylabel('RAM (kB)', color='#666')
                    if type in ['sacct_consumedenergy']:
                        ax_all_multi[rep-1].set_ylabel('energy (kJ)', color='#666')
                    ax_all_multi[rep-1].grid(True, axis='y')

                    ax_all_one.plot(x, values, lw=2, c=f"C{rep}", label=f"run{rep}")

            first_values_cleaned = self.remove_outliers(first_values)
            linear = self.get_linear_expectation(config, sum(first_values_cleaned)/len(first_values_cleaned))
            linear_inv = self.get_linear_expectation_inv(config, sum(first_values_cleaned)/len(first_values_cleaned))

            if type in ['sacct_consumedenergy']:
                ax_all_one.plot(x, linear_inv, lw=4, c=f"C{i}", alpha=0.25, label='linear')
            else:
                ax_all_one.plot(x, linear, lw=4, c=f"C{i}", alpha=0.25, label='linear')

            ax_all_one.legend(loc="upper right")
            for n in config["n_tasks"]:
                xticks.add(n)

            title = type
            fig_all_one.suptitle(f'{title}', fontsize=20)
            fig_all_one.canvas.manager.set_window_title(f'{title}')
            #fig_all.setp(plt.legend().get_texts(), color='#666')
            ax_all_one.set_xlabel('number of NEST processes', color='#666')
            ax_all_one.set_xscale('log')
            ax_all_one.get_xaxis().set_major_formatter(matplotlib.ticker.ScalarFormatter())
            ax_all_one.set_xticks(list(xticks))
            ax_all_one.set_ylabel('time (s)', color='#666')
            if type in ['sacct_averss', 'sacct_maxrss']:
                ax_all_one.set_ylabel('RAM (kB)', color='#666')
            if type in ['sacct_consumedenergy']:
                ax_all_one.set_ylabel('energy (kJ)', color='#666')

            ax_all_one.grid(True, axis='y')
            fig_all_one.tight_layout(pad=0.6, w_pad=0.25, h_pad=0.25)
            fig_all_one.savefig(f'{folder}/{type}-one.jpg')

            title = type
            fig_all_multi.suptitle(f'{title}', fontsize=20)
            fig_all_multi.canvas.manager.set_window_title(f'{title}')
            fig_all_multi.tight_layout(pad=0.6, w_pad=0.25, h_pad=0.25)
            fig_all_multi.savefig(f'{folder}/{type}-multi.jpg')

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
        for rep in range(1, config['repetitions']+1, 1):

            runtimes = [data[f"{rep}"][ntasks]['runtime']/3600 for ntasks in data[f"{rep}"]]
            ntasks = [int(ntasks.replace("_ntasks", "")) for ntasks in data[f"{rep}"]]
            nodehours = [a * b for a, b in zip(ntasks, runtimes)]
            first_values.append(nodehours[0])

            xticks = set()
            x = config["n_tasks"]
            ax_all.plot(x, nodehours, lw=2, c=f"C{rep}", label=f"run{rep}")

        first_values_cleaned = self.remove_outliers(first_values)
        linear = self.get_linear_expectation_inv(config, sum(first_values_cleaned)/len(first_values_cleaned)) #float(list(data_run.values())[0]['runtime']))
        ax_all.plot(x, linear, lw=4, c=f"C{i}", alpha=0.25, label='linear')

        ax_all.legend(loc="upper right")
        for n in config["n_tasks"]:
            xticks.add(n)
            # TODO: get number of neurons and connections from metadata and use in
            # subtitle

        title = "Node Hours"
        fig_all.suptitle(f'{title}', fontsize=20)
        fig_all.canvas.manager.set_window_title(f'{title}')
        #fig_all.setp(plt.legend().get_texts(), color='#666')
        ax_all.set_xlabel('number of NEST processes', color='#666')
        ax_all.set_xscale('log')
        ax_all.get_xaxis().set_major_formatter(matplotlib.ticker.ScalarFormatter())
        ax_all.set_xticks(list(xticks))
        ax_all.set_ylabel('node hours (h)', color='#666')
        ax_all.grid(True, axis='y')
        fig_all.tight_layout(pad=0.6, w_pad=0.25, h_pad=0.25)

        fig_all.savefig(f'{folder}/nodehours.jpg')

        plt.close('all')


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
