import nest


def create_PKJ(subCB):
    """PKJ

    Example:

    ::

        create_PKJ()
    """
    configuration = {}
    # Membrane potential in mV
    # configuration['V_m'] = 0.0
    # Leak reversal Potential (aka resting potential) in mV
    configuration['E_L'] = -68.0
    # Membrane Capacitance in pF
    configuration['C_m'] = 107.0
    # Refractory period in ms
    configuration['t_ref'] = 5.0
    # Threshold Potential in mV
    configuration['V_th'] = -55.0
    # Reset Potential in mV
    configuration['V_reset'] = -70.0
    # Excitatory reversal Potential in mV
    configuration['E_ex'] = 0.0
    # Inhibitory reversal Potential in mV
    configuration['E_in'] = -75.0
    # Leak Conductance in nS
    configuration['g_L'] = 2.32
    # Time constant of the excitatory synaptic exponential function in ms
    configuration['tau_syn_ex'] = 8.0
    # Time constant of the inhibitory synaptic exponential function in ms
    configuration['tau_syn_in'] = 10.0
    # Constant Current in pA
    configuration['I_e'] = 0.8 * (10**2)
    nest.CopyModel('iaf_cond_exp', subCB+'_layer_pkj', configuration)
