import nest


def create_BS(subCB):
    """BS

    Example:

    ::

        create_BS()
    """
    configuration = {}
    # Threshold Potential in mV
    configuration['V_th'] = -55.0
    # Reset Potential in mV
    configuration['V_reset'] = -70.0
    # Refractory period in ms
    configuration['t_ref'] = 2.5
    # Leak Conductance in nS
    configuration['g_L'] = 2.32
    # Membrane Capacitance in pF
    configuration['C_m'] = 107.0
    # Excitatory reversal Potential in mV
    configuration['E_ex'] = 0.0
    # Inhibitory reversal Potential in mV
    configuration['E_in'] = 0.0
    # Leak reversal Potential (aka resting potential) in mV
    configuration['E_L'] = -68.0
    # Synaptic Time Constant Excitatory Synapse in ms
    configuration['tau_syn_ex'] = 8.3
    # Synaptic Time Constant for Inhibitory Synapse in ms
    configuration['tau_syn_in'] = 1.0e-15
    # Constant Current in pA
    configuration['I_e'] = 0.0
    nest.CopyModel('iaf_cond_exp', subCB+'_layer_bs', configuration)
