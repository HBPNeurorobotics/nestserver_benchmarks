import nest


def create_VN(subCB):
    """VN

    Example:

    ::

        create_VN()
    """
    configuration = {}
    # Membrane potential in mV
    # configuration['V_m'] = 0.0
    # Leak reversal Potential (aka resting potential) in mV
    configuration['E_L'] = -56.0
    # Membrane Capacitance in pF
    configuration['C_m'] = 122.3
    # Refractory period in ms
    configuration['t_ref'] = 2.5
    # Threshold Potential in mV
    configuration['V_th'] = -38.8
    # Reset Potential in mV
    configuration['V_reset'] = -70.0
    # Excitatory reversal Potential in mV
    configuration['E_ex'] = 0.0
    # Inhibitory reversal Potential in mV
    configuration['E_in'] = -88.0
    # Leak Conductance in nS
    configuration['g_L'] = 1.63
    # Time constant of the excitatory synaptic exponential function in ms
    configuration['tau_syn_ex'] = 30.6
    # Time constant of the inhibitory synaptic exponential function in ms
    configuration['tau_syn_in'] = 42.3 
    # Constant Current in pA
    configuration['I_e'] = 3.0 * (10**2)
    nest.CopyModel('iaf_cond_exp', subCB+'_layer_vn', configuration)
