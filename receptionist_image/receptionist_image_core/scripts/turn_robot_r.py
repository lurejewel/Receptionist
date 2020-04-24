#!/usr/bin/env python
# -*- coding: utf-8 -*
import rospy
import roslib
from std_msgs.msg import Bool
from sensor_msgs.msg import RegionOfInterest
from geometry_msgs.msg import Twist

# /image/found_john
# /image/found_seat
# /image/roi
class turn_robot():

    def __init__(self):

        self.join_sub = rospy.Subscriber('/image/found_seat_pos',RegionOfInterest, self.roiCallback,queue_size=1)
        self.per_sub = rospy.Subscriber('/image/roi',RegionOfInterest, self.roiCallback,queue_size=1)
        self.roi_sub = rospy.Subscriber('/image/found_john',Bool, self.boolCallback,queue_size=1)

        self.cmd_pub = rospy.Publisher('cmd_vel_mux/input/navi',Twist,queue_size=1)
        self.time = 0
        self.time_turn = 2


    def roiCallback(self, msg):

        # msg = RegionOfInterest() [format disclaiming]
        if msg.width == 0 and msg.height == 0:
            self.time +=1
            if self.time == self.time_turn:
                self.time = 0
                vel = Twist()
                vel.angular.z = 1.0
                self.cmd_pub.publish(vel)
        elif 300 >= msg.width/2 + msg.x_offset:
            # 往左转
            vel = Twist()
            vel.angular.z = 0.2
            self.cmd_pub.publish(vel)
        elif 340 <= msg.width/2 + msg.x_offset:
            # 往右转
            vel = Twist()
            vel.angular.z = -0.2
            self.cmd_pub.publish(vel)


    def boolCallback(self, msg):

        if msg.data == False:
            vel = Twist()
            vel.angular.z = 1.0
            self.cmd_pub.publish(vel)


if __name__ == '__main__':

    rospy.init_node('turn_and_check', anonymous=True)
    turn = turn_robot()
    try:
        rospy.spin()
    except KeyboardInterrupt:
        print("CLOSE Turn")

