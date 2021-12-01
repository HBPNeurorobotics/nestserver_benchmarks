from gazebo_msgs.srv import ApplyJointEffort, JointRequest
import rospy

joint_clear_proxy = rospy.ServiceProxy("/gazebo/clear_joint_forces", JointRequest)
joint_effort_proxy = rospy.ServiceProxy("/gazebo/apply_joint_effort", ApplyJointEffort)
@nrp.MapVariable("apply_joint_effort_srv", initial_value=joint_effort_proxy)
@nrp.MapVariable("joint_clear_srv", initial_value=joint_clear_proxy)

@nrp.Robot2Neuron()
def jointeffort (t,
                apply_joint_effort_srv, joint_clear_srv):
    
    from gazebo_msgs.srv import ApplyJointEffortRequest
    
    ## Joint1
    effort_msg = ApplyJointEffortRequest()
    effort_msg.joint_name = 'joystick_world_joint'
    effort_msg.effort = -0.001
    effort_msg.start_time.secs = 0.0
    effort_msg.start_time.nsecs = 0.0
    effort_msg.duration.secs = 2.0
    effort_msg.duration.nsecs = 0.0
    
    joint_clear_srv.value('joystick_world_joint')
    feedback = apply_joint_effort_srv.value(effort_msg)    
   