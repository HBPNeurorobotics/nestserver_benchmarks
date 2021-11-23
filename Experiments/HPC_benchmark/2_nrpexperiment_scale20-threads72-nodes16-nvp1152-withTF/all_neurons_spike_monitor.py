import numpy as np
@nrp.MapSpikeSink("neuron_p_1", nrp.map_neurons(range(0,1000), lambda i: nrp.brain.record[i]), nrp.leaky_integrator_alpha)
@nrp.NeuronMonitor(nrp.brain.record, nrp.leaky_integrator_alpha)
def all_neurons_spike_monitor (t, neuron_p_1):
    all_neuron_mean_voltages = np.mean(neuron_p_1.voltage)
    clientLogger.info(all_neuron_mean_voltages)
    return True


