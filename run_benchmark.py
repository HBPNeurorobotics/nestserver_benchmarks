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

import helpers
import ast

class BenchmarkRunner:

    def __init__(self):

        self.nodelist = helpers.expand_nodelist()
        logger.info("Nodes in allocation: %s", self.nodelist)
        self.jobstep = -1
        self.running = False


    def start_nest(self, n):

        values = {
            'n_nodes_nest': n,
            'n_tasks_nest': 2 * n,
            'nodezero': self.nodelist[0],
            'jobid': os.environ.get("SLURM_JOB_ID"),
            'account': os.environ.get("SLURM_JOB_ACCOUNT"),
        }

        logger.info("Starting NEST")
        logger.info("  Nodes  : %s", n)

        with open(f"{os.getcwd()}/misc/nest.sh.tpl", 'r') as infile:
            with open(f'{self.rundir}/nest.sh', 'w') as outfile:
                outfile.write(f"{infile.read()}".format(**values))

        subprocess.Popen(["bash", f"{self.rundir}/nest.sh"])
        self.jobstep += 1
        time.sleep(10) # Give the NEST container some time to start


    def stop_nest(self):
        job_step_id = f"{os.environ.get('SLURM_JOB_ID')}.{self.jobstep}"
        logger.info("Canceling NEST: %s", job_step_id)
        logger.info("  Obtaining metadata from NEST")
        nest_info = self.get_nest_info()
        time.sleep(10)
        subprocess.call(["scancel", job_step_id])
        logger.info("  Called scancel, sleeping 30 seconds")
        time.sleep(30) # Wait for the job to die
        with open(f'{self.rundir}/metadata.yaml', 'w') as outfile:
            logger.info("  Obtaining metadata from sacct")
            run_info = self.get_sacct_info(job_step_id)
            run_info.update(nest_info)
            outfile.write(yaml.dump(run_info, default_flow_style=False))
        logger.info("  Cancelling complete")


    def get_sacct_info(self, job_step_id):
        fmt = "--format=Elapsed,AveRSS,MaxRSS"
        output = subprocess.check_output(["sacct", "-j", job_step_id, "-p", "--noheader", fmt])
        output = output.decode("utf-8").split("|")[:-1]
        elapsed = datetime.strptime(output[0], "%H:%M:%S") - datetime(1900, 1, 1)
        return {
            "sacct_elapsed": elapsed.total_seconds(),
            "sacct_averss": float(output[1].replace("K", "")),
            "sacct_maxrss": float(output[2].replace("K", "")),
        }


    def get_nest_info(self):
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


    def ps_fu(self):
        user = os.environ.get("USER")
        print(subprocess.Popen(["ps", "-fu", user]).communicate())


    def run(self):
        if 'n_nodes' not in config:
            n_nodes_max = int(os.environ.get("SLURM_NNODES"))
            n_nodes = [2**x for x in range(11) if 2**x < n_nodes_max]
        else:
            n_nodes = config['n_nodes']

        for n in n_nodes:
            logger.info(f"Running benchmark step with {n} nodes")
            self.rundir = f"{config['datadir']}/{n:02d}nodes"
            os.makedirs(self.rundir)
            self.start_nest(n)
            getattr(self, f"run_{config['testcase']}")(n)
            self.stop_nest()

        logger.info("Done!")


    def run_hpcbench_baseline(self, nprocs):
        """Baseline benchmark using only NEST Server and no NRP.

        This variant of the benchmark uses the same brain simulation script as the
        HPC benchmarks below, but instead of running the brain simulation by means
        of an experiment in the NRP, it sends the script directly to NEST Server.

        We consider this the baseline benchmark to compare all other runs of the
        HPC benchmarks to.

        """

        runtime_total = 0
        with open(f'{self.rundir}/step_time.dat', "w") as logfile:
            simtime = 20.0
            logger.info(f'Running hpcbench_base with {nprocs} processes, 2 per node')

            url = f"http://{self.nodelist[1]}:5000"
            headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
            response = requests.post(f'{url}/api/ResetKernel', json={}, headers=headers)

            tic = time.time()
            data = {'source': open('hpcbench_baseline.py').read()}
            response = requests.post(f'{url}/exec', json=data, headers=headers)
            exec_time = time.time() - tic
            runtime_total += exec_time
            logfile.write(f'{exec_time}\t# exec_time\n')

            times = {}
            data = {'t': simtime}
            for cycle in range(config['n_cycles_nest']):
                tic = time.time()
                response = requests.post(f'{url}/api/Simulate', json=data, headers=headers)
                sim_time = time.time() - tic
                runtime_total += sim_time
                times[f"cycle_time_{cycle}"] = sim_time

            for label, t in times.items():
                logfile.write(f'{t}\t# {label}\n')

        with open(f'{self.rundir}/total_time.dat', "w") as logfile:
            logfile.write(str(runtime_total))

        logger.info(f'  Done after t={runtime_total}')


    def stop_cb(self, status):

        if status['state'] == 'stopped' or status['state'] == 'halted':
            with open(f'{self.rundir}/total_time.dat', "w+") as logfile:
                logfile.write(str(time.time() - self.tic))
            self.running = False


    def run_hpcbench_notf(self, nprocs):
        """HPC benchmark via NRP without transfer functions.
        """
        """HPC benchmark via NRP with simple transfer function.

        The transfer function records and reads spikes from a certain
        subpopulation of the model. To have some load on the NRP side, we use the
        husky robot as body model.

        """
        logger.info("Running NRP - HPC benchmark with TF")
        self.running = True
        homedir = os.environ.get("HOME")
        fullpath = "{homedir}/nestserver_benchmarks/HPC_benchmark/scale20-threads72-nodes16-nvp1152-withoutTF"
        response_result = vc.import_experiment(fullpath)
        dict_content = ast.literal_eval(response_result.content.decode("UTF-8"))
        self.experiment = dict_content['destFolderName']
        vc.print_cloned_experiments()
        time.sleep(30)
        self.tic = time.time()
        self.sim = vc.launch_experiment(self.experiment, profiler='cle_step')
        self.sim.register_status_callback(self.stop_cb)
        self.sim.start()
        while self.running:
            time.sleep(0.5)
        #vc.delete_cloned_experiment(self.experiment)
        # TODO: make sure the simulation time is comparable to the one used in
        # the hpcbench_baseline test case

        # TODO: get profiling data using proxy rest api or copy it from the
        # backend



    def run_hpcbench_readspikes(self, nprocs):
        """HPC benchmark via NRP with simple transfer function.

        The transfer function records and reads spikes from a certain
        subpopulation of the model. To have some load on the NRP side, we use the
        husky robot as body model.

        """
        logger.info("Running NRP - HPC benchmark with TF")
        self.running = True
        homedir = os.environ.get("HOME")
        fullpath = "{homedir}/nestserver_benchmarks/HPC_benchmark/scale20-threads72-nodes16-nvp1152-withTF"
        response_result = vc.import_experiment(fullpath)
        dict_content = ast.literal_eval(response_result.content.decode("UTF-8"))
        self.experiment = dict_content['destFolderName']
        vc.print_cloned_experiments()
        time.sleep(30)
        self.tic = time.time()
        self.sim = vc.launch_experiment(self.experiment, profiler='cle_step')
        self.sim.register_status_callback(self.stop_cb)
        self.sim.start()
        while self.running:
            time.sleep(0.5)
        #vc.delete_cloned_experiment(self.experiment)
        # TODO: make sure the simulation time is comparable to the one used in
        # the hpcbench_baseline test case

        # TODO: get profiling data using proxy rest api or copy it from the
        # backend


    def run_robobrain():
        pass


if __name__ == '__main__':

    if len(sys.argv) != 2:
        "Usage: run_benchmarks.py <configfile>"

    FORMAT = '[%(asctime)-15s - %(user)-8s] %(message)s'
    logging.basicConfig(format=FORMAT)
    logger = logging.getLogger('BenchmarkRunner')

    config = helpers.get_config(sys.argv[1])
    secrets = helpers.get_secrets()

    if config["testcase"] != "hpcbench_baseline":
        vc = VirtualCoach(
            f"http://{config['nrp_frontend_ip']}",
            oidc_username=secrets['hbp_username'],
            oidc_password=secrets['hbp_password'],
        )

    runner = BenchmarkRunner()
    runner.run()
