#!/usr/bin/env python
# -*- coding: utf-8 -*-
import roslib
import rospy
import numpy as np
from aip import AipFace
from aip import AipBodyAnalysis
import cv2
import matplotlib.pyplot as plt
from std_msgs.msg import String
from std_msgs.msg import Int8
from std_msgs.msg import Bool
from sensor_msgs.msg import Image
from sensor_msgs.msg import RegionOfInterest
from cv_bridge import CvBridge, CvBridgeError

import os
import time
import base64
import copy

from control.msg import reception
from receptionist_image_msgs.msg import reception_image
from receptionist_image_msgs.msg import BoundingBox
from receptionist_image_msgs.msg import BoundingBoxes

#对于reception可以直接人体识别client_body，不需要挥手识别

#总体思路：先进行人体检测，再对人体进行人脸检测
# John的信息应该是可以提前录入的，先使用addface
# 在第一个人检测完之后将其信息也加入facegroup
# serving阶段需要按照年龄分配座位检测座位上的人client-face & seat？？
# 沙发的检测


class Guest:
    def __init__(self):
        self.name   = None
        self.age    = None
        self.image  = None
        self.gender = None
        self.drink  = None

class user:
    def __init__(self):
        self.user_id = None
        self.facenum = 0

FindGuest = 1
FindJohn = 2
FindSofa = 3

class Guest_Recognition():
    def __init__(self):

        rospy.init_node('receptionist_image')
        # rospy.on_shutdown(self.cleanup)
        self.rate = rospy.Rate(1)

        APP_ID = '18721308'
        API_KEY = 'lNQGdBNazTPv8LpSP4x0GQlI'
        SECRET_KEY = 'nW8grONY777n4I2KvpOVuKGDNiY03omI'
        self.client_face = AipFace(APP_ID, API_KEY, SECRET_KEY)
        self.client_body = AipBodyAnalysis(APP_ID, API_KEY, SECRET_KEY)
        self.bridge = CvBridge()
        self.image_type = "BASE64"
        self.filepath = "/home/lurejewel/catkin_ws/src/receptionist_image/receptionist_image_core/pictures/image.jpg"
        # self.filepath = "/home/tianyili/robocup/src/image.jpg"
        

        self.guest = Guest()

        self.john = user()
        self.john.user_id = 'john'
        self.john.facenum = 0

        self.guest1 = user()
        self.guest1.user_id = 'guest1'
        self.guest1.facenum = 0
        self.groupIdList = 'reception_group'

        self.options_body = {}
        self.options_body["type"] = "gender,age"
        self.options_face = {}
        self.options_face["face_field"] = "age,gender"
        self.options_face["max_face_num"] = 3
        self.options_face["face_type"] = "LIVE"
        # 
        self.boxes = BoundingBoxes()
        self.human_boxes = BoundingBoxes()
        self.sofa = BoundingBox()
        self.seat = RegionOfInterest()
        # 工作状态
        self.workstate = 0
        #发布器
        self.control_pub = rospy.Publisher("/control", reception, queue_size=1)
        self.roi_pub = rospy.Publisher('/image/roi',RegionOfInterest,queue_size=1)
        self.seat_pos = rospy.Publisher('/image/found_seat_pos',RegionOfInterest,queue_size=1)
        self.seat_pub = rospy.Publisher('/image/found_seat',Bool,queue_size=1)
        self.control_pub = rospy.Publisher("/control", reception, queue_size=1)
        self.introduce = rospy.Publisher('/image/found_john',Bool,queue_size=1)
        #订阅器
        self.control_sub = rospy.Subscriber("/control", reception, self.controlCallback, queue_size=1)
        self.sofa_sub = rospy.Subscriber("/darknet_ros/bounding_boxes", BoundingBoxes, self.sofaCallback, queue_size=1)
        self.img_sub = rospy.Subscriber("/usb_cam/image_raw", Image, self.imgCallback, queue_size=1)
        

        self.ROI = RegionOfInterest()

    
    def controlCallback(self, msg):
        if msg.NowTask == msg.GuestRecognition and msg.FinishState == False:
            print("===Start to find guest===")
            self.workstate = FindGuest
            
        elif msg.NowTask == msg.Introducing and msg.FinishState == False:
            print("===Start to find John===")
            self.workstate = FindJohn
            # self.can_speak(self.groupIdList)
            
            
        elif msg.NowTask == msg.Serving and msg.FinishState == False:
            print("===Start to find Sofa===")
            self.workstate = FindSofa

        else:
            # 其他情况不进行工作
            # 
            self.workstate = 0

	# 沙发检测
    def sofaCallback(self,msg):
        if self.workstate != FindSofa:
            return
        self.boxes = msg.bounding_boxes
        self.sofa = None
        self.human_boxes = []
        # 检查视野目标
        for box in self.boxes:
            if box.Class == 'bed':
                self.sofa = box
                break
        for box in self.boxes:
            if box.Class == 'person':
                self.human_boxes.append(box)
        # 判断空位置
        if self.sofa is not None:
            sofa_width = box.xmax - box.xmin
            hum_in_sofa = []
            if len(self.human_boxes) != 0:
                # 计算一个人的平均占据宽度
                hum_width = 0.0
                flag = 0
                for human in self.human_boxes:
                    # 人在沙发位置
                    if (human.xmax < self.sofa.xmax) and (human.xmin>self.sofa.xmin):
                        flag += 1
                        hum_width += human.xmax - human.xmin
                        hum_in_sofa.append(human)
                # 判断情况
                if flag == 0:
                    # 没有人——指向沙发
                    self.seat.x_offset = self.sofa.xmin
                    self.seat.width = self.sofa.xmax - self.sofa.xmin
                    self.seat.y_offset = self.sofa.ymin
                    self.seat.height = self.sofa.ymax - self.sofa.ymin
                    self.seat_pos.publish(self.seat)
                elif flag == 1:
                    # 只有一个人
                    dis_R = self.sofa.xmax - hum_in_sofa[0].xmax
                    dis_L = hum_in_sofa[0].xmin - self.sofa.xmin
                    if dis_R >= dis_L:
                        self.seat.x_offset = hum_in_sofa[0].xmax
                        self.seat.width = self.sofa.xmax - hum_in_sofa[0].xmax
                        self.seat.y_offset = self.sofa.ymin
                        self.seat.height = self.sofa.ymax - self.sofa.ymin
                        self.seat_pos.publish(self.seat)
                    else:
                        self.seat.x_offset = self.sofa.xmin
                        self.seat.width = hum_in_sofa[0].xmin - self.sofa.xmin
                        self.seat.y_offset = self.sofa.ymin
                        self.seat.height = self.sofa.ymax - self.sofa.ymin
                        self.seat_pos.publish(self.seat)
                else:
                    # 为人体数据排序——只需要按照一个边
                    hum_width = hum_width/flag
                    for i in range(len(hum_in_sofa)):
                        for j in range(0,len(hum_in_sofa)-1):
                            if hum_in_sofa[j].xmax > hum_in_sofa[j+1].xmax:
                                data = copy.deepcopy(hum_in_sofa[j+1])
                                hum_in_sofa[j+1] = hum_in_sofa[j]
                                hum_in_sofa[j] = data
                    # 检查每一个人的纵向差异
                    STATE = False
                    for i in range(len(hum_in_sofa-1)):
                        if hum_in_sofa[i].xmax - hum_in_sofa[i+1].xmin < hum_width:
                            continue
                        else:
                            self.seat.x_offset = hum_in_sofa[i].xmax
                            self.seat.width = hum_in_sofa[i+1].xmin
                            self.seat.y_offset = hum_in_sofa[i].ymin
                            self.seat.height = hum_in_sofa[i].ymax
                            self.seat_pos.publish(self.seat)
                            STATE = True
                    # 没有空余位置
                    if STATE == False:
                        self.seat.x_offset = 0
                        self.seat.width = 0
                        self.seat.y_offset = 0
                        self.seat.height =0
                        self.seat_pos.publish(self.seat)
            else:
                self.seat.x_offset = self.sofa.xmin
                self.seat.width = self.sofa.xmax - self.sofa.xmin
                self.seat.y_offset = self.sofa.ymin
                self.seat.height = self.sofa.ymax - self.sofa.ymin
                self.seat_pos.publish(self.seat)
        else:
            self.seat.x_offset = 0
            self.seat.width = 0
            self.seat.y_offset = 0
            self.seat.height =0
            self.seat_pos.publish(self.seat)
        print(self.seat.width/2 + self.seat.x_offset)
        if 300 < self.seat.width/2 + self.seat.x_offset < 340 :
            data = Bool()
            data.data = True
            self.seat_pub.publish(data)
        else:
            data = Bool()
            data.data = False
            self.seat_pub.publish(data)
            




    # 人体数据转换
    def msgtobody(self, image_msg):
        # 转为base64存储
        cv2.imwrite(self.filepath, image_msg)
        with open(self.filepath, 'rb') as fp:
            return fp.read()
    # 打开文件
    def fileopen(self, filepath):
        with open(filepath, 'rb') as fp:
            imgjson = base64.b64encode(fp.read())
            data = str(imgjson).encode('utf-8')
            return data
    # 判断人脸已知
    def judger(self ,result):
        if result['error_code'] == 0:
            result_sc = result['result']['user_list'][0]['score']
            # print(result_sc,type(result_sc))
            if result_sc > 80:
                # return result['result']['user_list'][0]['user_id']
                return True
            else:
                return False
        else:
            return False
        

    # 人脸库搜索   groupIdList="用户组名称"
    def face_search(self,filepath, groupIdList='reception_group'):  
        image = self.fileopen(filepath)
        imageType = "BASE64"
        result = self.client_face.search(image, imageType, groupIdList)
        print(result)  # 打印出所有信息
        print(result['result']['user_list'][0]['user_id'])
        return self.judger(result)
        # if result['error_code'] == 0:
        #     judger(result)
        # elif result['result'] == None:
        #     return False

    def imgCallback(self, image_msg):
        if self.workstate == FindGuest:
            try:
                cv_image = self.bridge.imgmsg_to_cv2(image_msg, "bgr8")
            except CvBridgeError as e:
                print(e)
            self.find_people(cv_image)
        if self.workstate == FindJohn:
            try:
                cv_image = self.bridge.imgmsg_to_cv2(image_msg, "bgr8")
            except CvBridgeError as e:
                print(e)
            self.can_speak(cv_image, self.groupIdList)


    """寻找人体并返回未知人员ROI"""
    def find_people(self, image):
        segment_data = self.msgtobody(image)
        result = self.client_body.bodyAttr(segment_data, self.options_body)
        if 'person_num' in result:
            person_num = result['person_num']
            # self.objpos_pub.publish()
        else:
            person_num=0
        print("THe number of person is " + str(person_num))
        if person_num == 0:
            self.ROI.x_offset = 0
            self.ROI.y_offset = 0
            self.ROI.width = 0
            self.ROI.height = 0
            self.roi_pub.publish(self.ROI)
        for num in range(0, int(person_num)):
            # 不认识的人则发布信息ROI
            cv2.imwrite(self.filepath, image)
            if self.face_search(self.filepath) == False:
                location = result['person_info'][num]['location']
                print(location)
                # print('upper_color:',upper_color,' upper_wear_fg:',upper_wear_fg)
                self.ROI.x_offset = int(location['left'])
                self.ROI.y_offset = int(location['top'])
                self.ROI.width = int(location['width'])
                self.ROI.height = int(location['height'])
                self.roi_pub.publish(self.ROI)
                print(self.ROI)
                msg = reception()
                msg.NowTask = msg.GuestRecognition
                msg.NextTask = msg.Requesting
                msg.FinishState = True
                self.control_pub.publish(msg)
     
    # 检查是否是被介绍者
    """判断是否为被介绍者"""
    def can_speak(self,image, groupIdList='reception_group'):
        # result = self.face_search(filepath,groupIdList)
        #     # 是已知人员可介绍
        # if result['score']>80:
        #     self.introduce.publish(True)
        cv2.imwrite(self.filepath, image)
        result = self.face_search(self.filepath,groupIdList)
        # 是已知人员可介绍
        # if result:
        self.introduce.publish(result)
        print('result:',result)

    def face_add(self, filepath, image_msg, groupid, userid):  # 人脸库增加 地址 组 用户
        image = self.fileopen(filepath)
        imageType = "BASE64"
        result = self.client.addUser(image, imageType, groupid, userid)
        if result['error_code'] == 0:
            print("增加人脸成功")
        else:
            print("增加人脸失败")
            print(result)



    def get_user_facenum(self, userid):
        if userid == 'john':
            return self.john
        else:
            return self.guest1

    def add_user(self, file_name, image_msg):
        cv2.imwrite(file_name, image_msg)
        search_result = self.face_search(file_name, 'reception_group')
        curusr = user()
        
        # 加入新人脸
        if search_result['error_code'] == 222207:
            userid = 'john'
            self.john.facenum += 1
            curusr = self.john
            
        elif  search_result['error_code'] == 0 :
            if search_result['result']['user_list'][0]['score'] < 80:
                # ---------------------------------------
                num = len(search_result['result']['user_list'][0])
                if num == 0:
                    userid = 'john'
                    self.john.facenum += 1
                    curusr = self.john
                elif num == 1:
                    userid = 'guest1'
                    self.guest1.facenum += 1
                    curusr = self.guest1

            # 旧人脸
            else:
                userid = search_result['result']['user_list'][0]['user_id']
                curusr = self.get_user_facenum(userid)
        # 加入人脸张数信息 未达到上限20则持续添加，否则不作处理
        if curusr.facenum == 0 and curusr.user_id:
            self.face_add(file_name, image_msg, 'reception_group', curusr.user_id)
            print("curusr --------------------------")
            # print(curusr.user_id , curusr.facenum)
        else:
            print('wrong')


    # def cleanup(self):
    #     self.soundhandle.stopAll()
    #     rospy.loginfo("Shutting down partybot node...")



if __name__ =='__main__':
    #初始化节点
    # rospy.init_node('Guest_Recognition')
    print('----------init----------')  
    Guest_Recognition()
    try:
        rospy.spin()
    except rospy.ROSInterruptException:
        rospy.loginfo("receptionist_image node terminated.")

