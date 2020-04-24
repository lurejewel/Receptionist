#!/usr/bin/env python
# -*- coding: utf-8 -*

"""

Receptionist.py

author: Jin Wei
last edit: 2020/3/23
procedure: 


"""

import rospy
import thread
from std_msgs.msg import Bool
from std_msgs.msg import Float32
from std_msgs.msg import Float64
from control.msg import reception

class arm_receptionist:

    def __init__(self):

        self.finish = Bool()
        self.finish.data = False
        
        # init the node
        rospy.init_node('arm')

        # publish command message to joints/servos of arm
        self.joint1 = rospy.Publisher('/waist_controller/command',Float64)    # positive angle: counterclockwise 
        self.joint2 = rospy.Publisher('/shoulder_controller/command',Float64) # positive angle: counterclockwise (look from the left)
        self.joint3 = rospy.Publisher('/elbow_controller/command',Float64)    # positive angle: same as above
        self.joint4 = rospy.Publisher('/wrist_controller/command',Float64)    # positive angle: same as above
        self.joint5 = rospy.Publisher('/hand_controller/command',Float64)     # positive angle: close the gripper
        self.pos1 = Float64()
        self.pos2 = Float64()
        self.pos3 = Float64()
        self.pos4 = Float64()
        self.pos5 = Float64()

        rospy.Subscriber('/speech/candidate_ready', Bool, self.introducingCallback)
        rospy.Subscriber('/image/found_seat', Bool, self.servingCallback)
        self.finish_pointing_pub = rospy.Publisher('/arm/finish_pointing', Bool)

        if self.finish.data == True: # no it is not working.
            rospy.loginfo("Arm part finished.")
            for i in range(5):
                finish_pointing_pub.publish(finish)
            self.finish.data = False

        rospy.spin()    

    def introducingCallback(self, msg):
    # Robot arm points at its right side after SPEECH part finishes its job
        if msg.data == True:
            # Manipulation...
            # Pointing at right side
            rospy.loginfo('Pointing at right side...')

            self.pos1 = -1.565 # NEED TO CHECK THE ZERO-POINT POSITION
            self.pos2 = -0.628
            self.pos3 = -0.593
            self.pos4 = -0.349
            self.pos5 = 0.0
            self.joint1.publish(self.pos1)
            self.joint2.publish(self.pos2)
            self.joint3.publish(self.pos3)
            self.joint4.publish(self.pos4)
            self.joint5.publish(self.pos5)
            rospy.sleep(10)        

            self.finish.data = True

            # wait for 5 sec and the arm goes back to initial pose
            thread.start_new_thread(self.back2init,())

    def servingCallback(self, msg):
    # Robot arm points forward after IMAGE part finishes its job
        if msg.data == True:
            # Manipulation ...
            # Pointing forward
            rospy.loginfo('Pointing forward...')		

	    self.pos1 = 0.0
	    self.pos2 = -0.628
	    self.pos3 = -0.593
	    self.pos4 = -0.349
	    self.pos5 = 0.0
	    self.joint1.publish(self.pos1)
	    self.joint2.publish(self.pos2)
	    self.joint3.publish(self.pos3)
	    self.joint4.publish(self.pos4)
	    self.joint5.publish(self.pos5)
	    rospy.sleep(10)

            self.finish.data = True

            # wait for 5 sec and the arm goes back to initial pose
            thread.start_new_thread(self.back2init,())

    def back2init(self):
        # Robot arm back to initial pose

        # Initial gesture of robot arm
        # This is the natural pose for the robot arm
        rospy.sleep(10) # wait for SPEECH part to finish which lasts for about 5 seconds
        rospy.loginfo('initial gesture of robot arm: back2init')

        self.pos1 = 0.0
        self.pos2 = 2.102
        self.pos3 = -2.439
        self.pos4 = -1.294
        self.pos5 = 0.0
        self.joint1.publish(self.pos1)
        self.joint2.publish(self.pos2)
        self.joint3.publish(self.pos3)
        self.joint4.publish(self.pos4)
        self.joint5.publish(self.pos5)
        

if __name__=="__main__":
    arm_receptionist()
