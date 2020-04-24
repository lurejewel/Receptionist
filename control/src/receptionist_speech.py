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
        self.drink = []
        self.name = []
        self.gender = [] # 1 for male and 0 for female
        print("will launch terminal")
        os.system("gnome-terminal -x bash -c 'rosrun xfei_asr speech_recognition'")
        self.sh = SoundClient(blocking = True)
        self.voice = rospy.get_param("~voice", "voice_kal_diphone")
        finish = rospy.Publisher('speech/intro_finish', Bool) #1 for done
        check_door = rospy.Publisher('speech/check_door', Bool)
        print "Launching subscriber"
        rospy.Subscriber("/arm/finish_pointing", Bool, self.introduce_Callback)
        rospy.Subscriber("/control", reception, self.receptionist_Callback)	

    def introduce_Callback(self, msg):
        if len(self.name) == 0:
            if self.gender[-1] == 0:
                introduce_content = 'Hi, John! This is {}, She likes to drink {}.'.format(self.name[-1], self.drink[-1])
            else :
                introduce_content = 'Hi, John! This is {}, He likes to drink {}.'.format(self.name[-1], self.drink[-1])
        else:
            if self.gender[-1] == 0:
                introduce_content = 'Hi, John and {}! This is {}, She likes to drink {}.'.format(self.name[0], self.name[-1], self.drink[-1])
            else :
                introduce_content = 'Hi, John and {}! This is {}, He likes to drink {}.'.format(self.name[0], self.name[-1], self.drink[-1]])
        self.sh.say(introduce_content, self.voice)
        finish_signal = False
        self.finish.publish(finish_signal)

    def receptionist_Callback(self,msg):
        if msg.NowTask == msg.Requesting:
            self.sh.say('Please tell me your name and what would you like to drink, sir', self.voice)
            rospy.Subscriber("/xunfei_to_control", String, self.xfeiCallback)

    def xfeiCallback(self,msg):
        if msg.data.strip()=='':
            self.sh.say("Sorry I did not hear what you just said clearly", self.voice)
            self.sh.say("please tell me again", self.voice)
        else:
            ans = str(msg.data)
            tokens = nltk.word_tokenize(ans)
            tokens = nltk.pos_tag(tokens)
            self.name.append("anonymous")
            self.drink.append("water")
            for token in tokens:
                if token[1] == "NNP":
                    self.name[-1] = token[0]
            if token[1] == "NN":
                self.drink[-1] = token[0]
                print("speaking...")
                #NN名词单数形式,NNP专有名词
            speak_content = 'Greetings! {}, I like to drink {}, too!'.format(self.name[-1], self.drink[-1])
            self.sh.say(speak_content, self.voice)
  
        

if __name__ == '__main__':
    rospy.init_node("receptionist_test", anonymous=True)
    rospy.loginfo('receptionist_test.py is running...')
    trans = speech_transform()
    rospy.spin()