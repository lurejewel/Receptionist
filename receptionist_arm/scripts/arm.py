#!/usr/bin/env python

"""
    arm.py - move robot arm according to predefined gestures
    author: Jeffery Too Chuan Tan
    edit:   Jin Wei

    note: 
    1 | the robot arm need time to execute the command, which means 'rospy.sleep' is necessary here
    2 | the number refers to the goal angle each joint would reach, not the angle each joint would rotate
    3 | zero-point-pose of waist joint: See the words 'AX-12A' from the left; and take care not to make twine wrapped

"""

import rospy
from std_msgs.msg import Float64

class Loop:
    def __init__(self):
        rospy.on_shutdown(self.cleanup)

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
	
	#rospy.loginfo('sleeping...')
	#rospy.sleep(10)

	# Initial gesture of robot arm
	# This is the natural pose for the robot arm
	rospy.loginfo('initial gesture of robot arm')
	self.pos1 = 1.565
	self.pos2 = 2.102
	self.pos3 = -2.439
	self.pos4 = -1.294
	self.pos5 = 0.0
	self.joint1.publish(self.pos1)
	self.joint2.publish(self.pos2)
	self.joint3.publish(self.pos3)
	self.joint4.publish(self.pos4)
	self.joint5.publish(self.pos5)
	rospy.sleep(2)

	while not rospy.is_shutdown():

		rospy.loginfo('gesture1')		
		# gesture 1
		self.pos1 = 0#0.559
		self.pos2 = 0#0.215
		self.pos3 = 0#-1.508
		self.pos4 = 0#-0.496
		self.pos5 = 0.45#0.0
		self.joint1.publish(self.pos1)
		self.joint2.publish(self.pos2)
		self.joint3.publish(self.pos3)
		self.joint4.publish(self.pos4)
		self.joint5.publish(self.pos5)
		rospy.sleep(10)#2
		
		rospy.loginfo('gesture2')		
		# gesture 2
		self.pos1 = 0#0.565
		self.pos2 = 0#-2.393
		self.pos3 = 0#-0.639
		self.pos4 = 0#1.335
		self.pos5 = 0#-0.430
		self.joint1.publish(self.pos1)
		self.joint2.publish(self.pos2)
		self.joint3.publish(self.pos3)
		self.joint4.publish(self.pos4)
		self.joint5.publish(self.pos5)
		rospy.sleep(10)#3

		rospy.loginfo('return to gesture1')		
		# gesture 1
		self.pos1 = 0#0.559
		self.pos2 = 0#0.215
		self.pos3 = 0#-1.508
		self.pos4 = 0#-0.496
		self.pos5 = 0.35#0.0
		self.joint1.publish(self.pos1)
		self.joint2.publish(self.pos2)
		self.joint3.publish(self.pos3)
		self.joint4.publish(self.pos4)
		self.joint5.publish(self.pos5)
		rospy.sleep(10)#2

		rospy.loginfo('return to initial gesture')		
		# initial gesture
		self.pos1 = 0.565
		self.pos2 = 2.102
		self.pos3 = -2.439
		self.pos4 = -1.294
		self.pos5 = 0.0
		self.joint1.publish(self.pos1)
		self.joint2.publish(self.pos2)
		self.joint3.publish(self.pos3)
		self.joint4.publish(self.pos4)
		self.joint5.publish(self.pos5)
		rospy.sleep(10)#3

    def cleanup(self):
        rospy.loginfo("Shutting down robot arm....")

if __name__=="__main__":
    rospy.init_node('arm')
    try:
        Loop()
        rospy.spin()
    except rospy.ROSInterruptException:
        pass

