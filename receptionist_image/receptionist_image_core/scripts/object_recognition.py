#!/usr/bin/env python
# encoding:utf-8

import requests
import base64
import numpy as np

'''
通用物体和场景识别
'''
# 视频的处理
''''主要问题是位置信息如何获取？返回结果里不包含位置坐标。。。又或者不需要位置信息，只要检测沙发上有无人员即可?'''
class sofa_dec:

    def __init__(self):
        self.APP_ID = '18941175'
        self.API_KEY = 'mss0TVMZGgrtoo6rT9GFG0DG'
        self.SECRET_KEY = 'Mn8uvXUwYhzfRRH7sZMnhmb3Ewrlm6wC'
        # filepath = "/Pictures/image.jpg"
        
    
    def token(self):
        host = 'https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id=' + self.API_KEY + '&client_secret=' + self.SECRET_KEY
        response = requests.get(host)
        print(response.json())
        if response:
            json_data = response.json()
            accessToken = json_data["access_token"]
            return accessToken

# token()
    def object_recognition(self):
        obj_seat = np.array(['沙发','座椅','椅子','凳子'])
        person = np.array(['男人','女人','衣服','人','衣'])
        request_url = "https://aip.baidubce.com/rest/2.0/image-classify/v2/advanced_general"
        # 二进制方式打开图片文件
        f = open('/home/ljc/sofa.png', 'rb')
        img = base64.b64encode(f.read())

        params = {"image":img}
        access_token = self.token()
        
        print(access_token)
        request_url = request_url + "?access_token=" + access_token
        headers = {'content-type': 'application/x-www-form-urlencoded'}
        response = requests.post(request_url, data=params, headers=headers)
        if response:
            json_data = response.json()
            # print('jsonda',type(json_data))
            # print(json_data['result'])
            result = json_data['result']
            result_num =  len(result)
            for key in result:
                if key['keyword'] in obj_seat:
                    return True
                # if key['keyword'] in person:
                #     return False

# object_recognition()
