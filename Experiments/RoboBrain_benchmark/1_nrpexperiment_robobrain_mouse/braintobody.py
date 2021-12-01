#-------------------------------------------------------------------------------
# GLOBAL VARIABLES
@nrp.MapVariable("muscle_actuation", initial_value=8*[0.], scope=nrp.GLOBAL)
@nrp.MapVariable("external_input", initial_value=0, scope=nrp.GLOBAL)
@nrp.MapVariable("counter", initial_value=1, scope=nrp.GLOBAL)
@nrp.MapVariable("flag", initial_value=False, scope=nrp.GLOBAL)
#-------------------------------------------------------------------------------
# SPIKE SOURCES
@nrp.MapSpikeSource("M1_L1_ENGC_in", nrp.brain.M1_L1_ENGC, nrp.poisson, delay=1.5)
@nrp.MapSpikeSource("M1_L23_CC_in", nrp.brain.M1_L23_CC, nrp.poisson, delay=1.5)
@nrp.MapSpikeSource("M1_L5A_CC_in", nrp.brain.M1_L5A_CC, nrp.poisson, delay=1.5)
#-------------------------------------------------------------------------------
# SPIKE SINKS
@nrp.MapSpikeSink("M1_L1_ENGC", nrp.brain.M1_L1_ENGC, nrp.leaky_integrator_alpha, delay=1.5)
@nrp.MapSpikeSink("M1_L1_SBC", nrp.brain.M1_L1_SBC, nrp.leaky_integrator_alpha, delay=1.5)

@nrp.MapSpikeSink("M1_L23_CC", nrp.brain.M1_L23_CC, nrp.leaky_integrator_alpha, delay=1.5)
@nrp.MapSpikeSink("M1_L23_PV", nrp.brain.M1_L23_PV, nrp.leaky_integrator_alpha, delay=1.5)
@nrp.MapSpikeSink("M1_L23_SST", nrp.brain.M1_L23_SST, nrp.leaky_integrator_alpha, delay=1.5)
@nrp.MapSpikeSink("M1_L23_VIP", nrp.brain.M1_L23_VIP, nrp.leaky_integrator_alpha, delay=1.5)

@nrp.MapSpikeSink("M1_L5A_CC", nrp.brain.M1_L5A_CC, nrp.leaky_integrator_alpha, delay=1.5)
@nrp.MapSpikeSink("M1_L5A_CS", nrp.brain.M1_L5A_CS, nrp.leaky_integrator_alpha, delay=1.5)
@nrp.MapSpikeSink("M1_L5A_CT", nrp.brain.M1_L5A_CT, nrp.leaky_integrator_alpha, delay=1.5)
@nrp.MapSpikeSink("M1_L5A_PV", nrp.brain.M1_L5A_PV, nrp.leaky_integrator_alpha, delay=1.5)
@nrp.MapSpikeSink("M1_L5A_SST", nrp.brain.M1_L5A_SST, nrp.leaky_integrator_alpha, delay=1.5)

@nrp.MapSpikeSink("M1_L5B_CC", nrp.brain.M1_L5B_CC, nrp.leaky_integrator_alpha, delay=1.5)
@nrp.MapSpikeSink("M1_L5B_CS", nrp.brain.M1_L5B_CS, nrp.leaky_integrator_alpha, delay=1.5)
@nrp.MapSpikeSink("M1_L5B_PT", nrp.brain.M1_L5B_PT, nrp.leaky_integrator_alpha, delay=1.5)
@nrp.MapSpikeSink("M1_L5B_PV", nrp.brain.M1_L5B_PV, nrp.leaky_integrator_alpha, delay=1.5)
@nrp.MapSpikeSink("M1_L5B_SST", nrp.brain.M1_L5B_SST, nrp.leaky_integrator_alpha, delay=1.5)

@nrp.MapSpikeSink("M1_L6_CT", nrp.brain.M1_L6_CT, nrp.leaky_integrator_alpha, delay=1.5)
@nrp.MapSpikeSink("M1_L6_PV", nrp.brain.M1_L6_PV, nrp.leaky_integrator_alpha, delay=1.5)
@nrp.MapSpikeSink("M1_L6_SST", nrp.brain.M1_L6_SST, nrp.leaky_integrator_alpha, delay=1.5)
@nrp.Robot2Neuron()
def braintobody (t, counter, flag,
                 muscle_actuation, external_input,
                 M1_L1_ENGC_in, M1_L23_CC_in, M1_L5A_CC_in, 
                 M1_L1_ENGC, M1_L1_SBC,
                 M1_L23_CC, M1_L23_PV, M1_L23_SST, M1_L23_VIP,
                 M1_L5A_CC, M1_L5A_CS, M1_L5A_CT, M1_L5A_PV, M1_L5A_SST,
                 M1_L5B_CC, M1_L5B_CS, M1_L5B_PT, M1_L5B_PV, M1_L5B_SST,
                 M1_L6_CT, M1_L6_PV, M1_L6_SST):
    
   
    #log the first timestep (20ms), each couple of second
    clientLogger.info('''Neuron Layer Output at Time: {}
                      M1_L1_ENGC: {}
                      M1_L1_SBC: {}
                      M1_L23_CC: {}
                      M1_L23_PV: {}
                      M1_L23_SST: {}
                      M1_L23_VIP: {}
                      M1_L5A_CC: {}
                      M1_L5A_CS: {}
                      M1_L5A_CT: {}
                      M1_L5A_PV: {}
                      M1_L5A_SST: {}
                      M1_L5B_CC: {}
                      M1_L5B_CS: {}
                      M1_L5B_PT: {}
                      M1_L5B_PV: {}
                      M1_L5B_SST: {}
                      M1_L6_CT: {}
                      M1_L6_PV: {}
                      M1_L6_SST: {}
                      '''.format(t,
                                 M1_L1_ENGC.voltage, M1_L1_SBC.voltage, 
                                 M1_L23_CC.voltage, M1_L23_PV.voltage, M1_L23_SST.voltage, M1_L23_VIP.voltage, 
                                 M1_L5A_CC.voltage, M1_L5A_CS.voltage, M1_L5A_CT.voltage, M1_L5A_PV.voltage,
                                 M1_L5A_SST.voltage, M1_L5B_CC.voltage, M1_L5B_CS.voltage, M1_L5B_PT.voltage, 
                                 M1_L5B_PV.voltage, M1_L5B_SST.voltage, 
                                 M1_L6_CT.voltage, M1_L6_PV.voltage, M1_L6_SST.voltage))
    
         
    M1_L1_ENGC_in.rate = 0.0

    if counter.value > 0 and counter.value % 150 == 0:
        if flag.value:
            flag.value = False
        else:
            flag.value = True
            
    if counter.value > 149:        
        if flag.value:
            clientLogger.advertise('''--> START Motor Cortex Spike Injections''', duration = 10000)
            M1_L1_ENGC_in.rate = 50000.0 
        elif not flag.value:
            clientLogger.advertise('''--> STOP Motor Cortex Spike Injections''', duration = 10000)
            M1_L1_ENGC_in.rate = 0.0 
        
    a = min(1, M1_L1_ENGC.voltage / 2.0)
    b = 1 - a
    
    muscle_actuation.value[6] = a
    muscle_actuation.value[1] = a
    muscle_actuation.value[4] = a
    muscle_actuation.value[0] = 0.2     
        
    M1_L23_CC_in.rate = 0.0 #external_input.value
    M1_L5A_CC_in.rate = 0.0 #external_input.value
    
    counter.value = counter.value + 1
    
