import nest


def create_GR(subCB):
    """GR

    Example:

    ::

        create_GR()
    """
    configuration = {}
    # Membrane potential in mV
    # configuration['V_m'] = 0.0
    # Leak reversal Potential (aka resting potential) in mV
    configuration['E_L'] = -58.0
    # Membrane Capacitance in pF
    configuration['C_m'] = 3.1
    # Refractory period in ms
    configuration['t_ref'] = 5.0
    # Threshold Potential in mV
    configuration['V_th'] = -35.0
    # Reset Potential in mV
    configuration['V_reset'] = -82.0
    # Excitatory reversal Potential in mV
    configuration['E_ex'] = 0.0
    # Inhibitory reversal Potential in mV
    configuration['E_in'] = -82.0
    # Leak Conductance in nS
    configuration['g_L'] = 0.43
    # Time constant of the excitatory synaptic exponential function in ms
    configuration['tau_syn_ex'] = 52.0 
    # Time constant of the inhibitory synaptic exponential function in ms
    configuration['tau_syn_in'] = 59.0 
    # Constant Current in pA
    configuration['I_e'] = 0.0
    print (subCB)
    nest.CopyModel('iaf_cond_exp', subCB+'_layer_gr', configuration)
