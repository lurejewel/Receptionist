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
from cv_bridge import CvBridge, CvBridgeError
import os
import numpy as np
import time
import base64
import copy
from receptionist_image_msg.msg import reception
from receptionist_image_msg.msg import reception_image

#对于reception可以直接人体识别client_body，不需要挥手识别

#总体思路：先进行人体检测，再对人体进行人脸检测
# John的信息应该是可以提前录入的，先使用addface
# 在第一个人检测完之后将其信息也加入facegroup
# serving阶段需要按照年龄分配座位检测座位上的人client-face & seat？？
# 沙发的检测


class Guest:
    def __init__(self):
        msg = reception_image()
        self.name = msg.name
        self.age = msg.age
        self.image = msg.image
        self.gender = msg.gender
        self.drink = msg.drink


class Guest_Recognition:
    def __init__(self):
        APP_ID = '18721308'
        API_KEY = 'lNQGdBNazTPv8LpSP4x0GQlI'
        SECRET_KEY = 'nW8grONY777n4I2KvpOVuKGDNiY03omI'
        self.client_face = AipFace(APP_ID, API_KEY, SECRET_KEY)
        self.client_body = AipBodyAnalysis(APP_ID, API_KEY, SECRET_KEY)
        self.image_type = "BASE64"
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

         #ros params
        self.sub_image_raw_topic_name           = None
        self.sub_destination_topic_name         = None
        self.pub_gender_recognition_topic_name  = None
        self.pub_object_position2d              = None
        # self.depth_img                          = np.array((480,640))
        self.get_params()
      

        #发布器
        self.objpos_pub = rospy.Publisher('/image/object_position2d',String,queue_size=1)

        #订阅器
        self.control_sub = rospy.Subscriber("/control", reception, self.controlCallback)
        self.speech_sub = rospy.Subscriber('/speech/check_door',String,self.find_people)
    

    # --------------
    def get_params(self):
        self.sub_image_raw_topic_name          = rospy.get_param('sub_image_raw_topic_name',          '/camera/rgb/image_raw')
        # self.sub_depth_image_topic_name        = rospy.get_param('sub_depth_image_topic_name',        '/camera/depth/image_raw')
        self.pub_gender_recognition_topic_name = rospy.get_param('pub_gender_recognition_topic_name', '/kamerider_image/gender_recognition')
        self.objpos_pub         = rospy.get_param('objpos_pub',         '/image/object_position2d')
        #定义R发布器和订阅器，话题名通过ROS PARAM参数服务器获取
        rospy.Subscriber(self.sub_image_raw_topic_name, Image, self.imageCallback)
        # rospy.Subscriber(self.sub_depth_image_topic_name, Image, self.depthCallback)

        self.pub_result = rospy.Publisher(self.pub_gender_recognition_topic_name, String, queue_size=1)
        # self.pub_person_pos = rospy.Publisher(self.pub_person_pos_topic_name, Pose,queue_size=1)
        self.objpos_pub = rospy.Publisher('/image/object_position2d',String,queue_size=1)

    def depthCallback(self, msg):
        bridge = CvBridge()
        try:
            cv_image = bridge.imgmsg_to_cv2(msg, '16UC1')
            self.depth_img = cv_image
        except CvBridgeError as e:
            print (e)
# -------------------------------------

    # 人体数据转换
    def msgtobody(self, image_msg, file_name='image_body.png'):
        # 转为base64存储
        cv2.imwrite(file_name, image_msg)
        with open(file_name, 'rb') as fp:
            return fp.read()


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
            return result['result']['user_list'][0]['user_id']
        else:
            return False
        

    """ 调用人脸视频比对人脸库 """
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

    def find_people():
        # msg_nav=msh
        # bridge = CvBridge()
        # try:
        #     cv_image = bridge.imgmsg_to_cv2(msg, 'bgr8')
        # except CvBridgeError as e:
        #     print (e)
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
                    else:
                        person_num=0

                    for num in range(0, int(person_num)):
                        print(num)
                        location = result['person_info'][num-1]['location']
                        print('upper_color:',upper_color,' upper_wear_fg:',upper_wear_fg)

                        A = (int(location['left']), int(location['top']))
                        B = (int(location['left']) + int(location['width'] ),int(location['top']))
                        C = ( int(location['left']) + int(location['width']),int(location['top']) + int(location['height']))
                        D = (int(location['left']) ,int(location['top']) + int(location['height'] ))

                        cv2.waitKey(1000)
                        # self.objpos_pub.publish()
                cnt+=1

            cv2.waitKey(0)

    def imageCallback(self, msg):
        if self.take_photo_signal:
            print ("[INFO] Start to take photo")
            bridge = CvBridge()
            self.take_photo_signal = False
            try:
                cv_image = bridge.imgmsg_to_cv2(msg, 'bgr8')
                cv2.imwrite(self.path_to_save_image, cv_image)
            except CvBridgeError as e:
                print (e)
            self.detection()



    # 挥手检测
    # image——输入的cv类型
    # gender——是否检查性别
    def detectWave(self, image, gender=False):
        #if time.time()-self.time < self.tau:
        #     return None
        # self.time = time.time()
        print("CHECK")
        data = self.msgtobody(image, "image_body.png")
        # ----------挥手检测----------
        result = self.client_body.bodyAnalysis(data)
        wave = []
        loaction = []
        point_t = []
        # 存在人
        if result['person_num'] > 0:
            id_ = -1
            # 对每个人进行检查
            for info in result['person_info']:
                id_+=1
                keypoint = info['body_parts']
                # 腕高
                if keypoint['right_elbow']['y'] > keypoint['right_wrist']['y']:
                    # 腕在外侧
                    if keypoint['right_wrist']['x'] < keypoint['right_shoulder']['x']:
                        wave.append(id_)
                        loc = []
                        loc.append(int(info['location']['left']))
                        loc.append(int(info['location']['left'] + info['location']['width']))
                        loc.append(int(info['location']['top']))
                        loc.append(int(info['location']['top']  + info['location']['height']))
                        loaction.append(copy.deepcopy(loc))
                # 腕高
                elif keypoint['left_elbow']['y'] > keypoint['left_wrist']['y']:
                    # 腕在外侧
                    if keypoint['left_wrist']['x'] > keypoint['left_shoulder']['x']:
                        wave.append(id_)
                        loc = []
                        loc.append(int(info['location']['left']))
                        loc.append(int(info['location']['left'] + info['location']['width']))
                        loc.append(int(info['location']['top']))
                        loc.append(int(info['location']['top']  + info['location']['height']))
                        loaction.append(copy.deepcopy(loc))

            # 存在挥手
            if len(loaction) > 0:
                # 女性检测
                # ----------性别检测----------
                if gender:
                    options = {}
                    options["type"] = "gender"
                    # 保证存在挥手
                    for locate in loaction:
                        img = image[locate[2]:locate[3],
                                    locate[0]:locate[1]]
                        img = self.msgtobody(img, "try__.png")
                        result = self.client_body.bodyAttr(img, options)
                        try:
                            result['person_info'][0]['attributes']['gender'] == "女性"
                        except:
                            continue
                        # 女性则直接返回女性位置
                        if result['person_info'][0]['attributes']['gender'] =="女性":
                            loc = []
                            loc.append(locate[0])
                            loc.append(locate[1])
                            loc.append(locate[2])
                            loc.append(locate[3])
                            return locate
                # 随机返回一个人
                locate = loaction[0]
                loc = []
                loc.append(locate[0])
                loc.append(locate[1])
                loc.append(locate[2])
                loc.append(locate[3])
                return locate

        return None





if __name__ =='__main__':
    #初始化节点
    rospy.init_node('Guest_Recognition')
# print（'----------init----------'）

    Guest_Recognition()
    rospy.spin()
