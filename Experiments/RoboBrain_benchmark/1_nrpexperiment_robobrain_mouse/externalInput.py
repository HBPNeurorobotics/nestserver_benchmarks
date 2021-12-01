@nrp.MapVariable("external_input", initial_value=0, scope=nrp.GLOBAL)
@nrp.Robot2Neuron()
def externalInput (t, external_input):
    external_input.value = 0.0#100000.0  # 10000.0
    clientLogger.advertise('helpme')