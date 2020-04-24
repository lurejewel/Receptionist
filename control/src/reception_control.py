#!/usr/bin/env python
# -*- coding: utf-8 -*

import os
import thread
import rospy
import roslib
from control.msg import reception

# DoorDetection -> EnterSite -> CannotOpen -> GuestRecognition -> Requesting -> Leading -> Introducing -> Serving -> Backward ─╮
#                                 ↑                                                                                                                                                                     │
#                                 ╰────────────────────────────────────────────────────────────────────────────────────────────╯(once again)

# DoorDetection: image
# EnterSite: navi
# CannotOpen: speech
# GuestRecognition: image
# Requesting: speech
# Leading: navi
# Introducing: image & navi -> speech(right side) -> arm -> speech(introducing)
# Serving: image & navi -> arm -> speeh
# Backward: navi

class Control:

    def __init__(self):
        msg = reception()
        self.now_state = msg.DoorDetection
        self.next_state = msg.EnterSite
        self.Return_time = 0
        self.need_help = False
        self.control_sub = rospy.Subscriber("/reception_control", reception, self.controlCallback)
        self.control_pub = rospy.Publisher("/reception_control", reception)
        
        msg.NowTask = msg.DoorDetection
        msg.NextTask = msg.EnterSite
        msg.NeedHelp = False
        msg.FinishState = False
        rospy.sleep(0.5)
        for i in range(5):
            self.control_pub.publish(msg)
            self.sh.say('i am ready to enter the arena.', self.voice)
        print("Start task Receptionist...")
        print("----------DoorDetection-----------")

    def controlCallback(self, msg):
        if msg.NeedHelp == True:
            print("Need help while there's no help way available.")
            # TODO:发布求救的节点（目前没有）

        elif msg.FinishState == True:
            
            n_msg = reception() #new msg
            # TODO:发布新的消息
            n_msg.NeedHelp = False
            n_msg.FinishState = False

            if msg.NowTask == n_msg.DoorDetection and self.now_state == n_msg.DoorDetection:
                n_msg.NowTask = n_msg.EnterSite
                n_msg.NextTask = n_msg.CannotOpen
                print("-------EnterSite-------")
                for i in range(5):
                    self.control_pub.publish(n_msg)
                self.now_state = n_msg.NowTask
                self.next_state= n_msg.NextTask

            elif msg.NowTask == n_msg.EnterSite and self.now_state == n_msg.EnterSite:
                n_msg.NowTask = n_msg.CannotOpen
                n_msg.NextTask = n_msg.GuestRecognition
                print("-------CannotOpen-------")
                for i in range(5):
                    self.control_pub.publish(n_msg)
                self.now_state = n_msg.NowTask
                self.next_state= n_msg.NextTask
                            
            elif msg.NowTask == n_msg.CannotOpen and self.now_state == n_msg.CannotOpen:
                n_msg.NowTask = n_msg.GuestRecognition
                n_msg.NextTask = n_msg.Requesting
                print("-------GuestRecognition-------")
                for i in range(5):
                    self.control_pub.publish(n_msg)
                self.now_state = n_msg.NowTask
                self.next_state= n_msg.NextTask

            elif msg.NowTask == n_msg.GuestRecognition and self.now_state == n_msg.GuestRecognition:
                n_msg.NowTask = n_msg.Requesting
                n_msg.NextTask = n_msg.Leading
                print("-------Requesting-------")
                for i in range(5):
                    self.control_pub.publish(n_msg)
                self.now_state = n_msg.NowTask
                self.next_state= n_msg.NextTask
                
            elif msg.NowTask == n_msg.Requesting and self.now_state == n_msg.Requesting:
                n_msg.NowTask = n_msg.Leading
                n_msg.NextTask = n_msg.Introducing
                print("-------Leading-------")
                for i in range(5):
                    self.control_pub.publish(n_msg)
                self.now_state = n_msg.NowTask
                self.next_state= n_msg.NextTask
                
            elif msg.NowTask == n_msg.Leading and self.now_state == n_msg.Leading:
                n_msg.NowTask = n_msg.Introducing
                n_msg.NextTask = n_msg.Serving
                print("-------Introducing-------")
                for i in range(5):
                    self.control_pub.publish(n_msg)
                self.now_state = n_msg.NowTask
                self.next_state= n_msg.NextTask
                
            elif msg.NowTask == n_msg.Introducing and self.now_state == n_msg.Introducing:
                n_msg.NowTask = n_msg.Serving
                n_msg.NextTask = n_msg.Backward
                print("-------Serving-------")
                thread.start_new_thread(self.open_yolo, ())
                rospy.sleep(2) # wait for node yolo to open
                for i in range(5):
                    self.control_pub.publish(n_msg)
                self.now_state = n_msg.NowTask
                self.next_state= n_msg.NextTask
                
            elif msg.NowTask == n_msg.Serving and self.now_state == n_msg.Serving:
                n_msg.NowTask = n_msg.Backward
                n_msg.NextTask = n_msg.GuestRecognition
                print("-------Backward-------")
                thread.start_new_thread(self.kill_yolo, ())
                for i in range(5):
                    self.control_pub.publish(n_msg)
                self.now_state = n_msg.NowTask
                self.next_state= n_msg.NextTask
                
            elif msg.NowTask == n_msg.Backward and self.now_state == n_msg.Backward:                
                self.Return_time += 1
                if self.Return_time >= 2:
                    print("1st guest task finished!")
                else:
                    n_msg.NowTask = n_msg.CannotOpen
                    n_msg.NextTask = n_msg.GuestRecognition
                    for i in range(5):
                        self.control_pub.publish(n_msg)
                    print("Once Again!")
                    print("-------CannotOpen-------")
                    self.now_state = n_msg.NowTask
                    self.next_state = n_msg.NextTask

    def open_yolo(self):
        # os.system("rosrun darknet_ros sofa_detect") # 好像不能直接指定节点名运行，还是要找到原.py文件
        rospy.loginfo("yolo opened")

    def kill_yolo(self):
        # os.system("rosnode kill sofa_detect")
        rospy.loginfo("yolo killed")

if __name__ == '__main__':
    rospy.init_node('control_task', anonymous=False)
    control_ = Control()
    try:
        rospy.spin()
    except KeyboardInterrupt:
        print("-------Shutting down-------")

