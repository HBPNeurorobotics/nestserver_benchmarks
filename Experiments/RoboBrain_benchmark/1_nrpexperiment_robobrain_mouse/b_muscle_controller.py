from std_msgs.msg import Float64
@nrp.MapVariable("muscle_actuation", initial_value=8*[0.], scope=nrp.GLOBAL)

@nrp.MapRobotPublisher("Foot1", Topic("/gazebo_muscle_interface/robobrain_mouse_with_joystick/Foot1/cmd_activation", Float64))
@nrp.MapRobotPublisher("Foot2", Topic("/gazebo_muscle_interface/robobrain_mouse_with_joystick/Foot2/cmd_activation", Float64))
@nrp.MapRobotPublisher("Radius1", Topic("/gazebo_muscle_interface/robobrain_mouse_with_joystick/Radius1/cmd_activation", Float64))
@nrp.MapRobotPublisher("Radius2", Topic("/gazebo_muscle_interface/robobrain_mouse_with_joystick/Radius2/cmd_activation", Float64))
@nrp.MapRobotPublisher("Humerus1", Topic("/gazebo_muscle_interface/robobrain_mouse_with_joystick/Humerus1/cmd_activation", Float64))
@nrp.MapRobotPublisher("Humerus2", Topic("/gazebo_muscle_interface/robobrain_mouse_with_joystick/Humerus2/cmd_activation", Float64))
@nrp.MapRobotPublisher("Humerus3", Topic("/gazebo_muscle_interface/robobrain_mouse_with_joystick/Humerus3/cmd_activation", Float64))
@nrp.MapRobotPublisher("Humerus4", Topic("/gazebo_muscle_interface/robobrain_mouse_with_joystick/Humerus4/cmd_activation", Float64))
@nrp.Robot2Neuron()
def b_muscle_controller (t, muscle_actuation, Foot1, Foot2, Humerus1, Humerus2, Humerus3, Humerus4, Radius1, Radius2):
    
    Foot1.send_message(muscle_actuation.value[0])
    Foot2.send_message(muscle_actuation.value[1])
    Radius1.send_message(muscle_actuation.value[2])
    Radius2.send_message(muscle_actuation.value[3])
    Humerus1.send_message(muscle_actuation.value[4])
    Humerus2.send_message(muscle_actuation.value[5])
    Humerus3.send_message(muscle_actuation.value[6])
    Humerus4.send_message(muscle_actuation.value[7])
