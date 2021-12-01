@nrp.NeuronMonitor(nrp.brain.M1_L1_ENGC + nrp.brain.M1_L1_SBC[0:400], nrp.spike_recorder )
def neuronMonitor(t):
    return True