#!/usr/bin/env python
# -*- coding: utf-8 -*-
import roslib
import rospy
from aip import AipFace
import base64
import json
import cv2
from PIL import Image


class user:
    def __init__(self):
        self.user_id
        self.facenum

class search:
    def __init__(self):
        self.APP_ID = '18721308'
        self.API_KEY = 'lNQGdBNazTPv8LpSP4x0GQlI'
        self.SECRET_KEY = 'nW8grONY777n4I2KvpOVuKGDNiY03omI'
        self.client = AipFace(self.APP_ID, self.API_KEY, self.SECRET_KEY)
        self.john = user()
        self.john.user_id='john'
        self.john.facenum=0
        self.guest1 = user()
        self.guest1.user_id='guest1'
        self.guest1.facenum=0
        self.groupid='reception_group'
        # 这里应该需要一个语音方面的信息
        self.introduce = rospy.Publisher('/image/introduce',bool,queue_size=1)
        """ 读取图片 """

        self.filepath = "/Pictures/image.jpg"

    # 人脸数据转换
    def msgtoface(self,image_msg, file_name='image_faces.png'):
        cv2.imwrite(file_name, image_msg)
        with open(file_name, 'rb') as fp:
            data = base64.b64encode(fp.read())
            # python2.7
            data = str(data).encode('utf-8')
            return data

    def fileopen(self, filePath):
        with open(filePath, 'rb') as fp:
            imgjson = base64.b64encode(fp.read())
        # python2.7
            data = str(imgjson).encode('utf-8')
            return data

    def judger(self,result):
        result_sc = result['result']['user_list'][0]['score']
        if result_sc > 80:
            # return result['result']['user_list'][0]['user_id']
            return True
        else:
            return False

    def face_search(self, filepath, groupIdList):  # 人脸库搜索   groupIdList="用户组名称"
        image = self.fileopen(filepath)
        imageType = "BASE64"
        result = self.client.search(image, imageType, groupIdList)
        if result['error_code'] == 0:
            self.judger(result)

    def can_speak(self,filepath,groupIdList):
        result = self.face_search(filepath,groupIdList)
            # 是已知人员可介绍
        if result['score']>80:
            self.introduce.publish(True)

    """  调用人脸视频添加建立人脸库  """
    def speak_to(self, window_name='image',camera_idx=0):
        cv2.namedWindow(window_name)
        #视频来源，可以来自一段已存好的视频，也可以直接来自USB摄像头
        cap = cv2.VideoCapture(camera_idx)

        while cap.isOpened():
            ok, frame = cap.read() #读取一帧数据
            if not ok:
                break
            c = cv2.waitKey(1000)#按q退出
            if c == ord('q'):
                break
            # cv2.imshow(window_name, frame)
            
            imageType = "BASE64"
            
            cv2.imwrite(self.filepath, frame)
            # add_user(filepath,frame)
            result = self.face_search(self.filepath,self.groupid)
            # 是已知人员可介绍
            if result['score']>80:
                self.introduce.publish(True)
                
            # face_add(filepath,frame ,'reception_group',userid)
            # result = client.search(image, imageType, 'test_group')
            # result = client.addUser(image, imageType, 'reception_group', 'john')
            # print(result)

        # cap.release()
        # cv2.destroyAllWindows()




if __name__ =='__main__':
    #初始化节点
    rospy.init_node('search')
# print（'----------init----------'）
    search()
    rospy.spin()





# face_add(filepath,'reception_group','john')
# face_search(filepath,'test_group')