import nest


def create_GO(subCB):
    """GO

    Example:

    ::

        create_GO()
    """
    configuration = {}
    # Membrane potential in mV
    # configuration['V_m'] = 0.0
    # Leak reversal Potential (aka resting potential) in mV
    configuration['E_L'] = -55.0
    # Membrane Capacitance in pF
    configuration['C_m'] = 28.0
    # Refractory period in ms
    configuration['t_ref'] = 5.0
    # Threshold Potential in mV
    configuration['V_th'] = -52.0
    # Reset Potential in mV
    configuration['V_reset'] = -72.7
    # Excitatory reversal Potential in mV
    configuration['E_ex'] = 0.0
    # Inhibitory reversal Potential in mV
    configuration['E_in'] = 0.0
    # Leak Conductance in nS
    configuration['g_L'] = 2.3
    # Time constant of the excitatory synaptic exponential function in ms
    configuration['tau_syn_ex'] = 170.0 
    # Time constant of the inhibitory synaptic exponential function in ms
    configuration['tau_syn_in'] = 1.0e-15 
    # Constant Current in pA
    configuration['I_e'] = 0.0
    nest.CopyModel('iaf_cond_exp', subCB+'_layer_go', configuration)
