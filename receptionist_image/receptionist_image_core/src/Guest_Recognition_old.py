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
from sensor_msgs.msg import Image
from sensor_msgs.msg import RegionOfInterest
from cv_bridge import CvBridge, CvBridgeError
import os
import numpy as np
import time
import base64
import copy
from receptionist_image_msgs.msg import reception
from receptionist_image_msgs.msg import reception_image

#对于reception可以直接人体识别client_body，不需要挥手识别

#总体思路：先进行人体检测，再对人体进行人脸检测
# John的信息应该是可以提前录入的，先使用addface
# 在第一个人检测完之后将其信息也加入facegroup
# serving阶段需要按照年龄分配座位检测座位上的人client-face & seat？？
# 沙发的检测


class Guest:
    def __init__(self):
        # msg = reception_image()
        self.name   = None
        self.age    = None
        self.image  = None
        self.gender = None
        self.drink  = None


class Guest_Recognition:
    def __init__(self):
        APP_ID = '18721308'
        API_KEY = 'lNQGdBNazTPv8LpSP4x0GQlI'
        SECRET_KEY = 'nW8grONY777n4I2KvpOVuKGDNiY03omI'
        self.client_face = AipFace(APP_ID, API_KEY, SECRET_KEY)
        self.client_body = AipBodyAnalysis(APP_ID, API_KEY, SECRET_KEY)
        self.image_type = "BASE64"
        filepath = "/Pictures/image.jpg"

        msg = reception_image()
        self.guest = Guest()
        # self.name = None
        # self.age = None
        # self.image = None
        # self.gender = None
        # self.drink = None

        self.options_body = {}
        self.options_body["type"] = "gender,upper_color,upper_wear_fg"
        self.options_face = {}
        self.options_face["face_field"] = "age,gender"
        self.options_face["max_face_num"] = 3
        self.options_face["face_type"] = "LIVE"
      

        #发布器
        self.roi_pub = rospy.Publisher('/image/roi',RegionOfInterest,queue_size=1)
        self.objpos_pub = rospy.Publisher('/image/object_position2d',String,queue_size=1)
        self.control_pub = rospy.Pubscriber("/control", reception, queue_size=1)
        self.speech_pub = rospy.Pubscriber('/speech/check_door',reception_image,self.find_people)
        #订阅器
        self.control_sub = rospy.Subscriber("/control", reception, self.controlCallback)
       
        self.ROI = RegionOfInterest()

    # 人体数据转换
    def msgtobody(self, image_msg, file_name='image_body.png'):
        # 转为base64存储
        cv2.imwrite(file_name, image_msg)
        with open(file_name, 'rb') as fp:
            return fp.read()
            
    def fileopen(self, filePath):
        with open(filePath, 'rb') as fp:
            imgjson = base64.b64encode(fp.read())
        # python2.7
            data = str(imgjson).encode('utf-8')
            return data

    # 人脸库搜索   groupIdList="用户组名称"
    def face_search(filepath, groupIdList):  
        image = fileopen(filepath)
        imageType = "BASE64"
        result = client.search(image, imageType, groupIdList)
        # print(result)  # 打印出所有信息
        print(result['result']['user_list'][0]['user_id'])

    # 判断人脸是否已知
    def judger(result):
        result_sc = result['result']['user_list'][0]['score']
        if result_sc > 80:
            # return result['result']['user_list'][0]['user_id']
            return True
        else:
            return False
        

    """ 调用人脸视频比对人脸库 是则return true"""
    def face_comparision(window_name='image',camera_idx=0):
        cv2.namedWindow(window_name)
        #视频来源，可以来自一段已存好的视频，也可以直接来自USB摄像头
        cap = cv2.VideoCapture(camera_idx)

        while cap.isOpened():
            ok, frame = cap.read() #读取一帧数据
            if not ok:
                break
            c = cv2.waitKey(100)#按q退出
            if c == ord('q'):
                break
            cv2.imshow(window_name, frame)
            base64_data = frame2base64(frame)
            image = str(base64_data, 'utf-8')
            imageType = "BASE64"

            result = client.search(image, imageType, 'test_group')

            if result['error_code'] == 0:
                judger(result)

        cap.release()
        cv2.destroyAllWindows()


"""寻找人体"""
    def find_people():
        cap = cv2.ViseoCapture(0)
        while cap.isOpened():
            ret, imgraw0 = cap.read()
            if ret:
                if cnt%10==0:
                    imgraw = cv2.resize(imgraw0, (512, 512))
                    cv2.imwrite(filepath, imgraw)
                    with open(filepath, "rb") as fp:
                        segment_data = fp.read()
                    result = client_body.bodyAttr(segment_data, options_body)
                    # print(result)

                    # 解析位置信息
                    if 'person_num' in result:
                        person_num = result['person_num']
                        # self.objpos_pub.publish()
                    else:
                        person_num=0

                    for num in range(0, int(person_num)):
                        print(num)
                        location = result['person_info'][num]['location']
                        print('upper_color:',upper_color,' upper_wear_fg:',upper_wear_fg)


                        self.ROI.x_offset = int(location['left'])
                        self.ROI.y_offset = int(location['top'])
                        self.ROI.width = int(location['width'])
                        self.ROI.height = int(location['height'])
                        self.roi_pub.publish(ROI)

                        cv2.waitKey(1000)
                        # self.objpos_pub.publish()
                cnt+=1

            cv2.waitKey(0)

    def imageCallback(self, msg):
        bridge = CvBridge()
        try:
            cv_image = bridge.imgmsg_to_cv2(msg, 'bgr8')
            cv2.imwrite(self.path_to_save_image, cv_image)
        except CvBridgeError as e:
            print (e)
        self.detection()









if __name__ =='__main__':
    #初始化节点
    rospy.init_node('Guest_Recognition')
# print（'----------init----------'）

    Guest_Recognition()
    rospy.spin()
