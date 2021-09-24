@nrp.MapSpikeSink("neuron_1", nrp.brain.record[1], nrp.leaky_integrator_alpha)
@nrp.NeuronMonitor(nrp.brain.record, nrp.leaky_integrator_alpha)
def all_neurons_spike_monitor(t, neuron_1):
    clientLogger.info(neuron_1.voltage)
    return True

