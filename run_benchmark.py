#!/usr/bin/env python3

from pynrp.virtual_coach import VirtualCoach
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

        #with open(f'misc/nest.sh.tpl', 'r') as infile:
        homedir = os.environ.get("HOME")
        fullpath = homedir + "/nestserver_benchmarks/misc/nest.sh.tpl"
        with open(fullpath, 'r') as infile:
            with open(f'{self.rundir}/nest.sh', 'w') as outfile:
                outfile.write(f"{infile.read()}".format(**values))

        self.nest_process = subprocess.Popen(["bash", f"{self.rundir}/nest.sh"])
        self.jobstep += 1
        time.sleep(10) # Give the NEST container some time to start


    def stop_nest(self):
        #print(subprocess.Popen(["ps", "-fu", "bp000193"]).communicate())
        job_step_id = f"{os.environ.get('SLURM_JOB_ID')}.{self.jobstep}"
        logger.info("Canceling NEST: %s", job_step_id)
        #print(subprocess.Popen(["scancel", job_step_id]))
        #subprocess.call(f"scancel {job_step_id}")
        time.sleep(10)
        subp = subprocess.call(["scancel",job_step_id])
        logger.info("  Job cancelled. Give it 30 seconds more to cleanup...")
        time.sleep(30) # Wait for the job to die


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

        with open(f'{self.rundir}/hpcbench_baseline.log', "w") as logfile:

            simtime = 20.0

            def log(line):
                logfile.write(line + '\n')

            logger.info(f'Running hpcbench_base, scale=10.0, nthreads=36, nprocs={nprocs}')

            url = f"http://{self.nodelist[1]}:5000"
            headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
            response = requests.post(f'{url}/api/ResetKernel', {}, headers=headers)

            tic = time.time()
            data = {'source': open('hpcbench_baseline.py').read()}
            response = requests.post(f'{url}/exec', json=data, headers=headers)
            exec_time = time.time() - tic
            log(f'{exec_time}\t# exec_time')

            data = {'t': simtime}
            sim_time_total = 0
            for cycle in range(config['n_cycles_nest']):
                tic = time.time()
                response = requests.post(f'{url}/api/Simulate', json=data, headers=headers)
                sim_time = time.time() - tic
                sim_time_total += sim_time
                log(f'{sim_time}\t# cycle_time_{cycle}')

            logger.info(f'  Done. t={sim_time_total}')


    def stop_cb(self, status):

        if status['state'] == 'stopped' or status['state'] == 'halted':
            with open(f'{self.rundir}/hpcbench.log', "w+") as logfile:
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
        fullpath = homedir + "/nestserver_benchmarks/HPC_benchmark/scale20-threads72-nodes16-nvp1152-withoutTF"
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
        fullpath = homedir + "/nestserver_benchmarks/HPC_benchmark/scale20-threads72-nodes16-nvp1152-withTF"
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

    vc = VirtualCoach(
        f"http://{config['nrp_frontend_ip']}",
        oidc_username=config['hbp_username'],
        oidc_password=config['hbp_password'],
    )

    runner = BenchmarkRunner()
    runner.run()
