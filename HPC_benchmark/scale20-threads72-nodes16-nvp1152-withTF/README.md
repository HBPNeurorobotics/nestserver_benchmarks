# HPC Benchmark: Random balanced network
# Scale: 20 (225000 neurons)
# Total number of virtual processes (nvp): 1152
# Total number of MPI processes: 16


## Pull images

```bash
module load sarus
sarus pull christopherbignamini/nest:jougs_nest_server_mpi

module use /scratch/snx3000/bignamic/EasyBuildInstall/modules/all/
module load skopeo
skopeo copy --insecure-policy docker://docker-registry.ebrains.eu/nrp-daint/nrp@sha256:1dfbe38dae84393402d30e1921cdf2f690beece62498389194ececc6a3aa525b docker-archive:nrp_nest_client.tar
sarus load nrp_nest_client.tar nrp_nest_client
```

## Launch NEST, TUNNEL and NRP

1. The following steps assume you have four terminals logged into Piz Daint

* In terminal 1, run
  ```
  cd $HOME/nrp_launch
  salloc -N 16 -J nrp-nest-scaleout -C 'mc&startx' -A ich004m --time=30 term1_nestsrv.sh
  ```
  (Set account-ID and time accordingly)

* In terminal 2, run
  ```
  cd $HOME/nrp_launch
  bash term2_tunnel.sh
  ```

* In terminal 3, run
  ```
  cd $HOME/nrp_launch
  bash term3_nrp.sh


## Launch Virtual Coach

2. Copy the compressed (zip) experiment file from your local workstation to your home directory in Piz Daint:

  scp nrp_experiment.zip bp000xxx@ela.cscs.ch:/users/bp000xxx
  (Where bp000xxx is your user account in Piz Daint)

3. in terminal 4, from your home directory run
   ```
  virtualenv pynrp
  source pynrp/bin/activate
  pip install pynrp
  python
  from pynrp.virtual_coach import VirtualCoach
    vc = VirtualCoach(' http://148.187.96.212', oidc_username='yourusername', oidc_password='yourpassword')
   ```
4. Import your experiment in the NRP
   ```
  vc.import_experiment("/users/bp000xxx/nrp_experiment.zip")
   ```
5. Verify that your experiment was successfully imported
   ```
  vc.print_cloned_experiments()
   ```
6. Launch the experiment
   ```
  sim = vc.launch_experiment("nrp_hpc_16nodes_0", profiler='cle_step')
   ```
7. Start the simulation
   ```
  sim.start()
   ```

8. Stop the simulation
   ```
  sim.stop()
   ```


  
  
