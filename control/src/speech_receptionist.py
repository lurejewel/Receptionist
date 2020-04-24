#! /usr/bin/env python

# -*- coding: utf-8 -*-
import roslib

'''

roslib.load_manifest ('speech')

roslib.load_manifest () reads the package manifest and sets up the python library path based on the package dependencies.

It's required for older rosbuild-based packages, but is no longer needed on catki

'''

import rospy
from std_msgs.msg import String
from std_msgs.msg import Bool
import os
import sys
import nltk
import time
import wave
import datetime
import pyaudio
from sound_play.libsoundplay import SoundClient
import random
from control.msg import reception

class speech_transform(object):

    def __init__(self):
        self.drink = ['coke']
        self.name = ['john']
        self.age = ['100'] 
        self.nowmission = 0
        # 0---ask for name and drink
        # 1---ask for check
        # 2---ask for name and drink again
        print("will launch terminal")
        os.system("gnome-terminal -x bash -c 'rosrun xfei_asr speech_recognition'")
        self.sh = SoundClient(blocking = True)
        self.voice = rospy.get_param("~voice", "voice_kal_diphone")
        finish = rospy.Publisher('speech/candidate_ready', Bool) #1 for done        
        print "Launching subscriber"
        rospy.Subscriber("/arm/finish_pointing", Bool, self.introduce_Callback)
        rospy.Subscriber("/control", reception, self.receptionist_Callback)	
        rospy.Subscriber("/image/found_john", Bool, self.foundCallback)
        rospy.Subscriber("/xunfei_to_control", String, self.xfeiCallback)
    def foundCallback(self, msg):
        self.sh.say('Please stand by my right side', self.voice)
        finish_signal = False
        self.finish.publish(finish_signal)
    def introduce_Callback(self, msg):
        if len(self.name) == 1:
            introduce_content = 'Hi, John! This is {}, {} likes to drink {}.'.format(self.name[-1], self.name[-1], self.drink[-1])
            intro_to_guest_content ='Hi, {}! This is John, John likes to drink {}.'.format(self.name[-1], self.drink[0])
        else:
            if len(self.name) == 2:
                introduce_content = 'Hi, John and {}! This is {}, {} likes to drink {}.'.format(self.name[0], self.name[-1], self.name[-1], self.drink[-1])
                intro_to_guest_content ='Hi, {}! This is John and {}, John likes to drink {} and {} likes to drink {}.'.format(self.name[-1], self.name[1],  self.drink[0], self.name[1], self.drink[1])
        self.sh.say(introduce_content, self.voice)
        self.sh.say(intro_to_guest_content, self.voice)

    def receptionist_Callback(self,msg):
        if msg.NowTask == msg.Requesting:
            self.name.append("anonymous")
            self.drink.append("water")
            self.age.append("100")
            self.sh.say('Please tell me your name and what would you like to drink, sir', self.voice)
            self.sh.say('If you are ready to response, please say jack to launch me first', self.voice)
            self.sh.nowmission = 0
        if msg.NowTask == msg.CannotOpen:
            self.sh.say('Please help me open the door', self.voice)

    def xfeiCallback(self,msg):

        if msg.data.strip()=='':
            self.sh.say("Sorry I did not hear what you just said clearly", self.voice)
            self.sh.say("please tell me again", self.voice)

        else:

            if self.nowmission == 0:
                ans = str(msg.data)
                tokens = nltk.word_tokenize(ans)
                tokens = nltk.pos_tag(tokens)
                for token in tokens:
                    if token[1] == "NNP":
                        self.name[-1] = token[0]
                    if token[1] == "NN":
                        self.drink[-1] = token[0]
                self.sh.say('Your name is {} and your favorite drink is {}, right?'.format(self.name[-1], self.drink[-1]), self.voice)
                self.sh.say('If so, please say yes. else say no. If you are ready to response, please say jack to launch me first', self.voice)
                self.nowmission = 1
            else:
                if self.nowmission == 1:
                    ans = str(msg.data)
                    tokens = nltk.word_tokenize(ans)
                    print(tokens)
                    for i in tokens:
                        if i == "no" or "NO" or "No":
                            self.sh.say("can you tell me again, please?", self.voice)
                            self.nowmission = 0
                            break  
                        else:
                            self.sh.say("can you tell me your age, please? If you are ready to response, please say jack to launch me first", self.voice)
                            self.nowmission = 2
                else:
                    if self.nowmission == 2:
                        ans = str(msg.data)
                        tokens = nltk.word_tokenize(ans)
                        tokens = nltk.pos_tag(tokens)
                        for token in tokens:
                            if token[1] == "CD":
                                self.age[-1] = token[0]
                                break
                        self.nowmission = 0

if __name__ == '__main__':
    rospy.init_node("receptionist_test", anonymous=True)
    rospy.loginfo('receptionist_test.py is running...')
    trans = speech_transform()
    rospy.spin()
