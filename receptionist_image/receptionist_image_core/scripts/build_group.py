#!/usr/bin/env python
# -*- coding: utf-8 -*-
# import roslib
# import rospy
from aip import AipFace
import base64
import json
import cv2
from PIL import Image



class user:
    def __init__(self):
        self.user_id=None

        self.facenum=None


class build_group:
    def __init__(self):
        # rospy.init_node('build_group')
        APP_ID = '18721308'
        API_KEY = 'lNQGdBNazTPv8LpSP4x0GQlI'
        SECRET_KEY = 'nW8grONY777n4I2KvpOVuKGDNiY03omI'
        self.client = AipFace(APP_ID, API_KEY, SECRET_KEY)
        self.john = user()
        self.john.user_id = 'john'
        self.john.facenum = 0
        self.guest1 = user()
        self.guest1.user_id = 'guest1'
        self.guest1.facenum = 0
        """ 读取图片 """

        self.filepath = "/home/lurejewel/catkin_ws/src/receptionist_image/receptionist_image_core/pictures/image.jpg"

    # 人脸数据转换
    def msgtoface(self, image_msg, file_name='image_faces.png'):
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

    def face_add(self, filepath, image_msg, groupid, userid):  # 人脸库增加 地址 组 用户
        image = self.fileopen(filepath)
        imageType = "BASE64"
        result = self.client.addUser(image, imageType, groupid, userid)
        if result['error_code'] == 0:
            print("增加人脸成功")
        else:
            print("增加人脸失败")
            # print(result)

    def face_search(self, filepath, groupIdList):  # 人脸库搜索   groupIdList="用户组名称"
        image = self.fileopen(filepath)
        imageType = "BASE64"
        result = self.client.search(image, imageType, groupIdList)
        print(result)  # 打印出所有信息
        # print(result['result']['user_list'][0]['user_id'])
        return result

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
                num = len(search_result['result']['user_list'][0]['user_id'])
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
    


    # """ 调用人脸视频添加建立人脸库 """

    def build_group(self, window_name='image', camera_idx=0):
        cv2.namedWindow(window_name)
        # 视频来源，可以来自一段已存好的视频，也可以直接来自USB摄像头
        cap = cv2.VideoCapture(camera_idx)
        cnt = 0
        while cap.isOpened():
            if cnt%10==0:
                ok, frame = cap.read()  # 读取一帧数据
                if not ok:
                    break
                c = cv2.waitKey(1000)  # 按q退出
                if c == ord('q'):
                    break
                cv2.imshow(window_name, frame)

                imageType = "BASE64"
                # cv2.imwrite(filepath, frame)
                self.add_user(self.filepath, frame)

                # self.face_add(self.filepath,frame ,'reception_group','john')
                
                # result = client.search(image, imageType, 'test_group')
                # result = client.addUser(image, imageType, 'reception_group', 'john')
                # print(result)
            cnt+=1
            

        cap.release()
        cv2.destroyAllWindows()


if __name__ == '__main__':
    # 初始化节点
    
    print('----------init----------')
    build = build_group()
    build.build_group()
    # try:
        
    #     rospy.spin()
    # except rospy.ROSInterruptException:
    #     rospy.loginfo("receptionist_image node terminated.")




# face_add(filepath,'reception_group','john')
# face_search(filepath,'test_group')
