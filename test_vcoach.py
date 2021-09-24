from pynrp.virtual_coach import VirtualCoach
vc = VirtualCoach(' http://148.187.96.212', oidc_username='cjimenez', oidc_password='Topsecret21$')

vc.import_experiment("HPC_benchmark/scale20-threads72-nodes16-nvp1152-withTF/NRP_experiment_0")
vc.print_cloned_experiments()
try:
    import_res = vc.import_experiment("HPC_benchmark/scale20-threads72-nodes16-nvp1152-withTF/NRP_experiment")
except:
    print("Experiment already cloned")
launch_res = vc.launch_experiment('NRP_experiment_0', profiler='cle_step')
vc.print_cloned_experiments()
