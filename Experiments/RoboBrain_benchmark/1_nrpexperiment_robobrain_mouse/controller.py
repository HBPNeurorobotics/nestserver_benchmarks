from std_msgs.msg import Float64

@nrp.MapVariable("muscle_actuation", initial_value=8*[0.], scope=nrp.GLOBAL)
@nrp.MapVariable("muscle_positions", initial_value=8*[0.], scope=nrp.GLOBAL)

@nrp.Robot2Neuron()
def controller (t,
               muscle_positions, muscle_actuation):       
        
    ## Send actuation values to muscle
    #muscle_actuation.value = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    if t < 1.0:
        muscle_actuation.value = [0.5, 0.9, 0.2, 0.4, 0.6, 0.8, 0.2, 0.6]