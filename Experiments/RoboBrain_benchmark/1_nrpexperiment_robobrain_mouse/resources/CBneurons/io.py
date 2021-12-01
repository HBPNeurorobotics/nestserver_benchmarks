import nest


def create_IO(subCB):
    """IO

    Example:

    ::

        create_IO()
    """
    configuration = {}
    # Membrane potential in mV
    # configuration['V_m'] = 0.0
    # Leak reversal Potential (aka resting potential) in mV
    configuration['E_L'] = -60.0
    # Membrane Capacitance in pF
    configuration['C_m'] = 10.0
    # Refractory period in ms
    configuration['t_ref'] = 10.0
    # Threshold Potential in mV
    configuration['V_th'] = -50.0
    # Reset Potential in mV
    configuration['V_reset'] = -75.0
    # Excitatory reversal Potential in mV
    configuration['E_ex'] = 0.0
    # Inhibitory reversal Potential in mV
    configuration['E_in'] = -75.0
    # Leak Conductance in nS
    configuration['g_L'] = 0.67 
    # Time constant of the excitatory synaptic exponential function in ms
    configuration['tau_syn_ex'] = 10.0 
    # Time constant of the inhibitory synaptic exponential function in ms
    configuration['tau_syn_in'] = 10.0
    # Constant Current in pA
    configuration['I_e'] = 0.0
    nest.CopyModel('iaf_cond_exp', subCB+'_layer_io', configuration)
