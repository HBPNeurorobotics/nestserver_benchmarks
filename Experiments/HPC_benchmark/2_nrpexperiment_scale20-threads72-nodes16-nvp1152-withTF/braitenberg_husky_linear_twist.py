"""
This module contains the transfer function which is responsible for determining the linear twist
component of the husky's movement based on the left and right wheel neuron
"""
import hbp_nrp_cle.tf_framework as nrp
from hbp_nrp_cle.robotsim.RobotInterface import Topic
import geometry_msgs.msg

#@nrp.MapSpikeSink("neuron_cluster", nrp.map_neurons(range(0,1000), lambda i: nrp.brain.actors[i]), nrp.leaky_integrator_alpha)
@nrp.MapSpikeSink("left_wheel_neuron", nrp.brain.actors[1], nrp.leaky_integrator_alpha)
@nrp.MapSpikeSink("right_wheel_neuron", nrp.brain.actors[2], nrp.leaky_integrator_alpha)
@nrp.Neuron2Robot(Topic('/husky/husky/cmd_vel', geometry_msgs.msg.Twist))
def linear_twist(t, left_wheel_neuron, right_wheel_neuron):
    """
    The transfer function which calculates the linear twist of the husky robot based on the
    voltage of left and right wheel neuron.

    :param t: the current simulation time
    :param left_wheel_neuron: the left wheel neuron device
    :param right_wheel_neuron: the right wheel neuron device
    :return: a geometry_msgs/Twist message setting the linear twist fo the husky robot movement.
    """

    return geometry_msgs.msg.Twist(
        linear=geometry_msgs.msg.Vector3(x=20.0 * min(left_wheel_neuron.voltage, right_wheel_neuron.voltage), y=0.0,
                                         z=0.0), angular=geometry_msgs.msg.Vector3(x=0.0, y=0.0, z=100.0 * (
            right_wheel_neuron.voltage - left_wheel_neuron.voltage)))
