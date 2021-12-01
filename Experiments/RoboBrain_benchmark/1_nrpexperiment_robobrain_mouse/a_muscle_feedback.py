from gazebo_ros_muscle_interface.msg import MuscleStates

@nrp.MapVariable("muscle_efforts", initial_value=None, scope=nrp.GLOBAL)
@nrp.MapVariable("muscle_positions", initial_value=None, scope=nrp.GLOBAL)
@nrp.MapVariable("muscle_velocities", initial_value=None, scope=nrp.GLOBAL)
@nrp.MapVariable("initial_muscle_length", initial_value=None, scope=nrp.GLOBAL)
@nrp.MapRobotSubscriber('muscle_states_msg', Topic('/gazebo_muscle_interface/robobrain_mouse/muscle_states', MuscleStates))
@nrp.Robot2Neuron()
def a_muscle_feedback (t, muscle_states_msg, muscle_velocities, muscle_positions, muscle_efforts, initial_muscle_length):
    import math
    
    # get muscle states
    muscle_states = dict((m.name, m) for m in muscle_states_msg.value.muscles)

    # fill muscle states into dictionaries
    positions = {}
    velocities = {}
    efforts = {}

    for m_name, m_values in muscle_states.items():
        positions.update({m_name: m_values.length})
        velocities.update({m_name: m_values.lengthening_speed})
        efforts.update({m_name: m_values.force})

    # get initial length
    if isinstance(initial_muscle_length.value, type(None)):
        initial_muscle_length.value = positions.values()

    # origin in the center position:
    muscle_positions.value = [value - initial_muscle_length.value[idx] for idx, value in enumerate(positions.values())]

    muscle_velocities.value = list(velocities.values())
    muscle_efforts.value = list(efforts.values())

