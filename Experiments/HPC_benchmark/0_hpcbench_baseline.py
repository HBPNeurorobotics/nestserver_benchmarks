# -*- coding: utf-8 -*-
#
# hpc_benchmark.py
#
# This file is part of NEST.
#
# Copyright (C) 2004 The NEST Initiative
#
# NEST is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# NEST is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with NEST.  If not, see <http://www.gnu.org/licenses/>.


"""
Random balanced network HPC benchmark
--------------------------------------

This script produces a balanced random network of `scale*11250` neurons in
which the excitatory-excitatory neurons exhibit STDP with
multiplicative depression and power-law potentiation. A mutual
equilibrium is obtained between the activity dynamics (low rate in
asynchronous irregular regime) and the synaptic weight distribution
(unimodal). The number of incoming connections per neuron is fixed
and independent of network size (indegree=11250).

This is the standard network investigated in [1]_, [2]_, [3]_.

A note on scaling
~~~~~~~~~~~~~~~~~~

This benchmark was originally developed for very large-scale simulations on
supercomputers with more than 1 million neurons in the network and
11.250 incoming synapses per neuron. For such large networks, synaptic input
to a single neuron will be little correlated across inputs and network
activity will remain stable over long periods of time.

The original network size corresponds to a scale parameter of 100 or more.
In order to make it possible to test this benchmark script on desktop
computers, the scale parameter is set to 1 below, while the number of
11.250 incoming synapses per neuron is retained. In this limit, correlations
in input to neurons are large and will lead to increasing synaptic weights.
Over time, network dynamics will therefore become unstable and all neurons
in the network will fire in synchrony, leading to extremely slow simulation
speeds.

Therefore, the presimulation time is reduced to 50 ms below and the
simulation time to 250 ms, while we usually use 100 ms presimulation and
1000 ms simulation time.

For meaningful use of this benchmark, you should use a scale > 10 and check
that the firing rate reported at the end of the benchmark is below 10 spikes
per second.

References
~~~~~~~~~~~~

.. [1] Morrison A, Aertsen A, Diesmann M (2007). Spike-timing-dependent
       plasticity in balanced random networks. Neural Comput 19(6):1437-67
.. [2] Helias et al (2012). Supercomputers ready for use as discovery machines
       for neuroscience. Front. Neuroinform. 6:26
.. [3] Kunkel et al (2014). Spiking network simulation code for petascale
       computers. Front. Neuroinform. 8:78

"""


M_INFO = 10
M_ERROR = 30


###############################################################################
# Parameter section
# Define all relevant parameters: changes should be made here


params = {
    'nthreads': 36,         # local number of threads per process
    'scale': 20,            # scaling factor of the network size 1.
                            # total network size = scale*11250 neurons
    'simtime': 250.,        # total simulation time in ms (250)
    'presimtime': 50.,      # simulation time until reaching equilibrium (50)
    'dt': 0.1,              # simulation step (0.1)
    'record_spikes': True,  # switch to record spikes of excitatory
                            # neurons to file
    'path_name': '.',       # path where all files will have to be written
    'log_file': 'log',      # naming scheme for the log files
}


###############################################################################
# For compatiblity with earlier benchmarks, we require a rise time of
# ``t_rise = 1.700759 ms`` and we choose ``tau_syn`` to achieve this for given
# ``tau_m``. This requires numerical inversion of the expression for ``t_rise``
# in ``convert_synapse_weight``. We computed this value once and hard-code
# it here.


tau_syn = 0.32582722403722841


brunel_params = {
    'NE': int(9000 * params['scale']),  # number of excitatory neurons 9000
    'NI': int(2250 * params['scale']),  # number of inhibitory neurons 2250

    'Nrec': 1000,  # number of neurons to record spikes from

    'model_params': {  # Set variables for iaf_psc_alpha
        'E_L': 0.0,  # Resting membrane potential(mV)
        'C_m': 250.0,  # Capacity of the membrane(pF)
        'tau_m': 10.0,  # Membrane time constant(ms)
        't_ref': 0.5,  # Duration of refractory period(ms)
        'V_th': 20.0,  # Threshold(mV)
        'V_reset': 0.0,  # Reset Potential(mV)
        # time const. postsynaptic excitatory currents(ms)
        'tau_syn_ex': tau_syn,
        # time const. postsynaptic inhibitory currents(ms)
        'tau_syn_in': tau_syn,
        'tau_minus': 30.0,  # time constant for STDP(depression)
        # V can be randomly initialized see below
        'V_m': 5.7  # mean value of membrane potential
    },

    ####################################################################
    # Note that Kunkel et al. (2014) report different values. The values
    # in the paper were used for the benchmarks on K, the values given
    # here were used for the benchmark on JUQUEEN.

    'randomize_Vm': True,
    'mean_potential': 5.7,
    'sigma_potential': 7.2,

    'delay': 1.5,  # synaptic delay, all connections(ms)

    # synaptic weight
    'JE': 0.14,  # peak of EPSP

    'sigma_w': 3.47,  # standard dev. of E->E synapses(pA)
    'g': -5.0,

    'stdp_params': {
        'delay': 1.5,
        'alpha': 0.0513,
        'lambda': 0.1,  # STDP step size
        'mu': 0.4,  # STDP weight dependence exponent(potentiation)
        'tau_plus': 15.0,  # time constant for potentiation
    },

    'eta': 1.685,  # scaling of external stimulus
    'filestem': params['path_name']
}

###############################################################################
# Function Section


#def build_network(logger):
def build_network():
    """Builds the network including setting of simulation and neuron
    parameters, creation of neurons and connections

    Requires an instance of Logger as argument

    """
    global M_INFO, brunel_params, params, tau_syn

    tic = time.time()  # start timer on construction

    # unpack a few variables for convenience
    NE = brunel_params['NE']
    NI = brunel_params['NI']
    model_params = brunel_params['model_params']
    stdp_params = brunel_params['stdp_params']

    # set global kernel parameters
    nest.SetKernelStatus({
        'local_num_threads': params['nthreads'],
        'resolution': params['dt'],
        'overwrite_files': True})

    nest.SetDefaults('iaf_psc_alpha', model_params)

    nest.message(M_INFO, 'build_network', 'Creating excitatory population.')
    E_neurons = nest.Create('iaf_psc_alpha', NE)

    nest.message(M_INFO, 'build_network', 'Creating inhibitory population.')
    I_neurons = nest.Create('iaf_psc_alpha', NI)

    if brunel_params['randomize_Vm']:
        nest.message(M_INFO, 'build_network',
                     'Randomizing membrane potentials.')

        random_vm = nest.random.normal(brunel_params['mean_potential'],
                                       brunel_params['sigma_potential'])
        # TODO: The following hangs, printing "_guarded_writes"
        # nest.GetLocalNodeCollection(E_neurons).V_m = random_vm
        # nest.GetLocalNodeCollection(I_neurons).V_m = random_vm
        nest.SetStatus(nest.GetLocalNodeCollection(E_neurons), "V_m", random_vm)
        nest.SetStatus(nest.GetLocalNodeCollection(I_neurons), "V_m", random_vm)

    # number of incoming excitatory connections
    CE = int(1. * NE / params['scale'])
    # number of incomining inhibitory connections
    CI = int(1. * NI / params['scale'])

    nest.message(M_INFO, 'build_network',
                 'Creating excitatory stimulus generator.')

    # Convert synapse weight from mV to pA
    conversion_factor = 325.78285940386394
    JE_pA = conversion_factor * brunel_params['JE']

    nu_thresh = model_params['V_th'] / (
        CE * model_params['tau_m'] / model_params['C_m'] *
        JE_pA * math.exp(1.) * tau_syn)
    nu_ext = nu_thresh * brunel_params['eta']

    E_stimulus = nest.Create('poisson_generator', 1, {
                             'rate': nu_ext * CE * 1000.})

    nest.message(M_INFO, 'build_network',
                 'Creating excitatory spike recorder.')

    nest.SetDefaults('static_synapse_hpc', {'delay': brunel_params['delay']})
    nest.CopyModel('static_synapse_hpc', 'syn_std')
    nest.CopyModel('static_synapse_hpc', 'syn_ex',
                   {'weight': JE_pA})
    nest.CopyModel('static_synapse_hpc', 'syn_in',
                   {'weight': brunel_params['g'] * JE_pA})

    stdp_params['weight'] = JE_pA
    nest.SetDefaults('stdp_pl_synapse_hom_hpc', stdp_params)

    nest.message(M_INFO, 'build_network', 'Connecting stimulus generators.')

    # Connect Poisson generator to neuron

    nest.Connect(E_stimulus, E_neurons, {'rule': 'all_to_all'},
                 {'synapse_model': 'syn_ex'})
    nest.Connect(E_stimulus, I_neurons, {'rule': 'all_to_all'},
                 {'synapse_model': 'syn_ex'})

    nest.message(M_INFO, 'build_network',
                 'Connecting excitatory -> excitatory population.')

    nest.Connect(E_neurons, E_neurons,
                 {'rule': 'fixed_indegree', 'indegree': CE,
                  'allow_autapses': False, 'allow_multapses': True},
                 {'synapse_model': 'stdp_pl_synapse_hom_hpc'})

    nest.message(M_INFO, 'build_network',
                 'Connecting inhibitory -> excitatory population.')

    nest.Connect(I_neurons, E_neurons,
                 {'rule': 'fixed_indegree', 'indegree': CI,
                  'allow_autapses': False, 'allow_multapses': True},
                 {'synapse_model': 'syn_in'})

    nest.message(M_INFO, 'build_network',
                 'Connecting excitatory -> inhibitory population.')

    nest.Connect(E_neurons, I_neurons,
                 {'rule': 'fixed_indegree', 'indegree': CE,
                  'allow_autapses': False, 'allow_multapses': True},
                 {'synapse_model': 'syn_ex'})

    nest.message(M_INFO, 'build_network',
                 'Connecting inhibitory -> inhibitory population.')

    nest.Connect(I_neurons, I_neurons,
                 {'rule': 'fixed_indegree', 'indegree': CI,
                  'allow_autapses': False, 'allow_multapses': True},
                 {'synapse_model': 'syn_in'})

    
    return E_neurons, I_neurons

#class Logger(object):
#    """Logger context manager used to properly log memory and timing
#    information from network simulations.
#
#    """
#
#    def __init__(self, file_name):
#        # copy output to cout for ranks 0..max_rank_cout-1
#        self.max_rank_cout = 5
#        # write to log files for ranks 0..max_rank_log-1
#        self.max_rank_log = 30
#        self.line_counter = 0
#        self.file_name = file_name
#
#    def __enter__(self):
#        if nest.Rank() < self.max_rank_log:
#
#            # convert rank to string, prepend 0 if necessary to make
#            # numbers equally wide for all ranks
#            rank = '{:0' + str(len(str(self.max_rank_log))) + '}'
#            fn = '{fn}_{rank}.dat'.format(
#                fn=self.file_name, rank=rank.format(nest.Rank()))
#
#            self.f = open(fn, 'w')
#
#        return self
#
#    def log(self, value):
#        if nest.Rank() < self.max_rank_log:
#            line = '{lc} {rank} {value} \n'.format(
#                lc=self.line_counter, rank=nest.Rank(), value=value)
#            self.f.write(line)
#            self.line_counter += 1
#
#        if nest.Rank() < self.max_rank_cout:
#            print(str(nest.Rank()) + ' ' + value + '\n')
#
#    def __exit__(self, exc_type, exc_val, traceback):
#        if nest.Rank() < self.max_rank_log:
#            self.f.close()


nest.ResetKernel()
nest.set_verbosity(M_INFO)

E_neurons, I_neurons = build_network()

#tic = time.time()
#nest.SetKernelStatus({"min_delay": 1.0})
#nest.Simulate(params['presimtime'])
#PreparationTime = time.time() - tic

#logger.log(str(memory_thisjob()) + ' # virt_mem_after_presim')
#logger.log(str(PreparationTime) + ' # presim_time')

#tic = time.time()
#nest.Simulate(params['simtime'])
#SimCPUTime = time.time() - tic

#logger.log(str(memory_thisjob()) + ' # virt_mem_after_sim')
#logger.log(str(SimCPUTime) + ' # sim_time')

#if params['record_spikes']:
#    logger.log(str(compute_rate(sr)) + ' # average rate')

print(nest.GetKernelStatus())

#circuit = E_neurons[:50] + I_neurons[:50]
subcircuit = E_neurons[:50] + I_neurons[:50]
populations = {'circuit':subcircuit}

