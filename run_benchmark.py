#!/usr/bin/env python3

from pynrp.virtual_coach import VirtualCoach
from datetime import datetime
import ruamel.yaml as yaml
import subprocess
import requests
import logging
import signal
import time
import sys
import os
import math

import helpers
import ast


class BenchmarkRunner:

    def __init__(self, rundir):

        self.nodelist = helpers.expand_nodelist()
        logger.info("Nodes in allocation: %s", self.nodelist)
        self.jobstep = -1
        self.running = False
        self.working_dir = os.getcwd()
        self.rundir = rundir

    def start_nest(self, ntasks):
        """
        Starts the NEST container with the given number of tasks,
        two tasks on each node.
        :param ntasks: Number of NEST tasks to run in total
        """

        values = {
            'n_nodes_nest': math.ceil(float(ntasks)/2),
            'n_tasks_nest': ntasks,
            'nodezero': self.nodelist[0],
            'jobid': os.environ.get("SLURM_JOB_ID"),
            'account': os.environ.get("SLURM_JOB_ACCOUNT"),
        }
        values['working_dir'] = os.getcwd()

        logger.info("Starting NEST")
        logger.info("  NEST tasks  : %s", ntasks)

        with open(self.working_dir + "/misc/nest.sh.tpl", 'r') as infile:
            with open(f'{self.ntasks_rundir}/nest.sh', 'w') as outfile:
                outfile.write(f"{infile.read()}".format(**values))

        subprocess.Popen(["bash", f"{self.ntasks_rundir}/nest.sh"])
        self.jobstep += 1
        time.sleep(60)  # Give the NEST container some time to start

    def stop_nest(self):
        """
        Stops NEST on all nodes and retrieves info data
        """

        job_step_id = f"{os.environ.get('SLURM_JOB_ID')}.{self.jobstep}"
        logger.info("Canceling NEST: %s", job_step_id)
        logger.info("  Obtaining metadata from NEST")
        nest_info = self.get_nest_info()
        time.sleep(10)
        subprocess.call(["scancel", job_step_id])
        logger.info("  Called scancel, sleeping 600 seconds")
        time.sleep(600)  # Wait for the job to die
        with open(f'{self.ntasks_rundir}/metadata.yaml', 'w') as outfile:
            logger.info("  Obtaining metadata from sacct")
            run_info = self.get_sacct_info(job_step_id)
            run_info.update(nest_info)
            outfile.write(yaml.dump(run_info, default_flow_style=False))
        logger.info("  Cancelling complete")

    def get_sacct_info(self, job_step_id):
        """
        Collects benchmark relevant data from sacct
        :param job_step_id: ID of the current job
        """
        
        fmt = "--format=Elapsed,AveRSS,MaxRSS,ConsumedEnergy"
        sacct_cmd = ["sacct", "-j", job_step_id, "-p", "--noheader", fmt]
        output = subprocess.check_output(sacct_cmd)
        output = output.decode("utf-8").split("|")[:-1]
        elapsed = datetime.strptime(output[0], "%H:%M:%S") - datetime(1900, 1, 1)
        return {
            "sacct_elapsed": elapsed.total_seconds(),
            "sacct_averss": float(output[1].replace("K", "").replace("M", "000")),
            "sacct_maxrss": float(output[2].replace("K", "").replace("M", "000")),
            "sacct_consumedenergy": float(output[3].replace("K", "").replace("M", "000"))
        }

    def get_nest_info(self):
        """
        Collects benchmark relevant info from NEST
        """

        url = f"http://{self.nodelist[1]}:5000"
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        response = requests.post(f'{url}/api/GetKernelStatus', json={}, headers=headers)
        return {
            "nest_time_create": response.json()["time_construction_create"],
            "nest_time_connect": response.json()["time_construction_connect"],
            "nest_time_last_simulate": response.json()["time_simulate"],
            "nest_num_nodes": response.json()["network_size"],
            "nest_num_connections": response.json()["num_connections"],
            "nest_num_processes": response.json()["num_processes"],
            "nest_local_num_threads": response.json()["local_num_threads"],
            "nest_time_simulated": response.json()["biological_time"],
        }
   
    def run(self):
        """
        Runs the benchmark
        """

        if 'n_tasks' not in config:
            n_nodes_max = int(os.environ.get("SLURM_NNODES"))
            n_tasks = [2**x for x in range(22) if 2**x < n_nodes_max*2]
        else:
            n_tasks = config['n_tasks']

        for n in n_tasks:
            logger.info(f"Running {config['testcase']} benchmark step with {n} NEST tasks")
            self.ntasks_rundir = f"{self.rundir}/{n:02d}_ntasks"
            os.makedirs(self.ntasks_rundir)
            self.start_nest(n)
            getattr(self, f"run_{config['testcase']}")(n)
            self.stop_nest()

        logger.info("Benchmarks done!")
 
    def run_nrp_benchmark(self, experiment_path):
        """
        Runs a benchmark experiment in the NRP
        :param experiment_path: Experiment path of the experiment that shall be 
                                imported and run.
        """

        vc = VirtualCoach(
            f"http://{config['nrp_frontend_ip']}",
            oidc_username=secrets['hbp_username'],
            oidc_password=secrets['hbp_password'],
        )

        # Import Experiment
        self.running = True
        response_result = vc.import_experiment(experiment_path)
        dict_content = ast.literal_eval(response_result.content.decode("UTF-8"))
        self.experiment = dict_content['destFolderName']
        vc.print_cloned_experiments()
        time.sleep(30)
        
        # Launch Experiment
        self.tic = time.time()

        self.sim = vc.launch_experiment(self.experiment, server='148.187.148.198-port-8080', profiler='cle_step')
        self.sim.register_status_callback(self.stop_cb)
        self.sim.start()
        while self.running:
            time.sleep(0.5)

        time.sleep(20)

        self.retrieve_nrp_profiler_data(self.experiment)

        # Delete Experiment after run
        vc.delete_cloned_experiment(self.experiment)

    def stop_cb(self, status):
        """
        NRP callback of the VirtualCoach as a helper executed when experiment 
        status changes.
        :param status: New status of the experiment
        """

        if status['state'] == 'stopped' or status['state'] == 'halted':
            with open(f'{self.ntasks_rundir}/total_time.dat', "w+") as logfile:
                logfile.write(str(time.time() - self.tic))
            self.running = False

    def retrieve_nrp_profiler_data(self, experiment_id):
        """
        Retrieves the experiment profiler data after a benchmark run.
        :param experiment_id: Experiment ID that data shall be retrieved from.
        """

        vc = VirtualCoach(
            f"http://{config['nrp_frontend_ip']}",
            oidc_username=secrets['hbp_username'],
            oidc_password=secrets['hbp_password'],
        )

        file_path = os.path.join(self.ntasks_rundir,"cle_time_profile_0.csv")
        logger.info("Saving CLE profiler data from experiment: {} to {}".format(experiment_id, file_path))
        cle_step_data = vc.get_last_run_file(experiment_id, 'profiler', 'cle_time_profile_0.csv')
        with open(file_path, "wb") as f_data:
            f_data.write(cle_step_data)

        # vc.print_experiment_run_files('experiment_name_id', 'profiler', 0)

        # TODO: Store profiler data in f'{self.ntasks_rundir}' and delete the experiment
        # vc.get_last_run_file('experiment_name_id', 'profiler', 'cle_time_profile.csv')
        # vc.delete_cloned_experiment(self.experiment)
        # self.experiment = None

        # vc.print_experiment_runs_files('experiment_name_id', 'profiler')
        # vc.get_experiment_run_file('experiment_name_id', 'profiler', 0, 'cle_time_profile.csv')
        # vc.print_last_run_files('experiment_name_id', 'profiler')
        # vc.get_last_run_file('experiment_name_id', 'profiler', 'cle_time_profile.csv')

    def run_hpcbench_baseline(self, ntasks):
        """
        Baseline benchmark using only NEST Server and no NRP.

        This variant of the benchmark uses the same brain simulation script as
        the HPC benchmarks below, but instead of running the brain simulation
        by means of an experiment in the NRP, it sends the script directly to
        NEST Server.

        We consider this the baseline benchmark to compare all other runs of
        the HPC benchmarks to.
        :param ntasks: NEST tasks to run the benchmark on
        """

        simtime = 20.0
        logger.info(f'Running hpcbench_base with {ntasks} processes, 2 per node')

        url = f"http://{self.nodelist[1]}:5000"
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        requests.post(f'{url}/api/ResetKernel', json={}, headers=headers)

        tic = time.time()
        data = {'source': open('Experiments/HPC_benchmark/0_hpcbench_baseline.py').read()}
        requests.post(f'{url}/exec', json=data, headers=headers)
        with open(f'{self.ntasks_rundir}/exec_time.dat', "w") as logfile:
            logfile.write(str(time.time() - tic))

        sim_times = []
        data = {'t': simtime}
        for cycle in range(config['n_cycles_nest']):
            tic = time.time()
            requests.post(f'{url}/api/Simulate', json=data, headers=headers)
            sim_times.append(time.time() - tic)

        with open(f'{self.ntasks_rundir}/step_time.dat', "w") as logfile:
            d
            logfile.write(f'brainstep\n')
            for t in sim_times:
                logfile.write(f"{t}\n")

        with open(f'{self.ntasks_rundir}/total_time.dat', "w") as logfile:
            logfile.write(str(sum(sim_times)))

        logger.info(f'  Done after t={sum(sim_times)}')

    def run_hpcbench_notf(self, ntasks):
        """
        HPC benchmark via NRP without transfer functions.
        :param ntasks: NEST tasks to run the benchmark on
        """

        logger.info(f"Running NRP - HPC benchmark without TF with {ntasks} processes, 2 per node")
        experiment_path = os.path.join(self.working_dir, "Experiments/HPC_benchmark/1_nrpexperiment_scale20-nvp1152-withoutTF")
        self.run_nrp_benchmark(experiment_path)

    def run_hpcbench_readspikes(self, ntasks):
        """
        HPC benchmark via NRP with simple transfer function.

        The transfer function records and reads spikes from a certain
        subpopulation of the model. To have some load on the NRP side, we use the
        husky robot as body model.
        :param ntasks: NEST tasks to run the benchmark on
        """

        logger.info(f"Running NRP - HPC benchmark with TF with {ntasks} processes, 2 per node")
        experiment_path = os.path.join(self.working_dir, "Experiments/HPC_benchmark/2_nrpexperiment_scale20-nvp1152-withTF")
        self.run_nrp_benchmark(experiment_path)

    def run_robobrain(self, ntasks):
        """
        RoboBrain benchmark experiment in the NRP consising of a musculoskeletal
        rodent model with 8 muscles and a brain model with 1Million+ Neurons.
        """
        logger.info(f"Running NRP - RoboBrain benchmark with TF with {ntasks} processes, 2 per node")
        experiment_path = os.path.join(self.working_dir, "Experiments/RoboBrain_benchmark/1_nrpexperiment_robobrain_mouse")
        self.run_nrp_benchmark(experiment_path)

        pass


if __name__ == '__main__':

    if len(sys.argv) != 2:
        "Usage: run_benchmarks.py <configfile>"

    FORMAT = '[%(asctime)-15s - %(user)-8s] %(message)s'
    logging.basicConfig(format=FORMAT)
    logger = logging.getLogger('BenchmarkRunner')

    config = helpers.get_config(sys.argv[1])
    rundir = sys.argv[2]
    secrets = helpers.get_secrets()

    logger.info('BF in here')
    runner = BenchmarkRunner(rundir)
    runner.run()
    
