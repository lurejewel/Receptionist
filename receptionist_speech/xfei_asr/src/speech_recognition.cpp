#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <unistd.h>
#include "qisr.h"
#include "msp_cmn.h"
#include "msp_errors.h"
#include "speech_recognizer.h"
#include <iconv.h>
#include"std_msgs/String.h"
#include "ros/ros.h"
#include "std_msgs/String.h"
#include <sound_play/sound_play.h>


#define FRAME_LEN   640 
#define BUFFER_SIZE 4096

int wakeupFlag   = 0 ;
int flag_ok = 0 ;
int flag_no = 0 ;
static void show_result(char *string, char is_over)
{
    flag_ok=1;   
    printf("\rResult: [ %s ]", string);
    if(is_over)
        putchar('\n');
}

static char *g_result = NULL;
static unsigned int g_buffersize = BUFFER_SIZE;

void on_result(const char *result, char is_last)
{
    if (result) {
        size_t left = g_buffersize - 1 - strlen(g_result);
        size_t size = strlen(result);
        if (left < size) {
            g_result = (char*)realloc(g_result, g_buffersize + BUFFER_SIZE);
            if (g_result)
                g_buffersize += BUFFER_SIZE;
            else {
                printf("mem alloc failed\n");
                return;
            }
        }
        strncat(g_result, result, size);
        show_result(g_result, is_last);
    }
}

void on_speech_begin()
{
    if (g_result)
    {
        free(g_result);
    }
    g_result = (char*)malloc(BUFFER_SIZE);
    g_buffersize = BUFFER_SIZE;
    memset(g_result, 0, g_buffersize);

    printf("Start Listening...\n");
    
   
}
void on_speech_end(int reason)
{
    if (reason == END_REASON_VAD_DETECT)
        printf("\nSpeaking done \n");
    else
        printf("\nRecognizer error %d\n", reason);
}

/* demo recognize the audio from microphone */
static void demo_mic(const char* session_begin_params)
{
    int errcode;
    int i = 0;

    struct speech_rec iat;

    struct speech_rec_notifier recnotifier = {
        on_result,
        on_speech_begin,
        on_speech_end
    };

    errcode = sr_init(&iat, session_begin_params, SR_MIC, &recnotifier);
    if (errcode) {
        flag_no=1;
        printf("speech recognizer init failed\n");
        return;
    }
    errcode = sr_start_listening(&iat);
    if (errcode) {
        flag_no=1;
        printf("start listen failed %d\n", errcode);
       
    }
    /* demo 10 seconds recording */
    while(i++ < 5)
        sleep(1);
    errcode = sr_stop_listening(&iat);
    if (errcode) {
        flag_no=1;
        printf("stop listening failed %d\n", errcode);
    }

    sr_uninit(&iat);
}


/* main thread: start/stop record ; query the result of recgonization.
 * record thread: record callback(data write)
 * helper thread: ui(keystroke detection)
 */

void WakeUp(const std_msgs::String::ConstPtr& msg)
{
	    if(msg->data=="jack"||msg->data=="jack ")
    {
        printf("waking up\r\n");
        usleep(700*1000);
        wakeupFlag=1;
    }
    
}

int main(int argc, char* argv[])
{
    // 初始化ROS
    ros::init(argc, argv, "voiceRecognition");
    ros::NodeHandle n;
    ros::Rate loop_rate(10);
    sound_play::SoundClient sound_client;

    // 声明Publisher和Subscriber
    // 订阅唤醒语音识别的信号
    ros::Subscriber wakeUpSub = n.subscribe("/kws_data", 1000, WakeUp);   
    // 订阅唤醒语音识别的信号    
    ros::Publisher pub_recognition_result = n.advertise<std_msgs::String>("/xunfei_to_control", 1);  
    printf("Sleeping......\n");
    int count=0;
    while(ros::ok())
    {	
		//bool temp_bool =true;
        // 语音识别唤醒
        if (wakeupFlag){
            printf("Wakeup...\n");
            sound_client.playWave("/home/lurejewel/catkin_ws/src/receptionist_speech/xfei_asr/sounds/question_start_signal.wav");
            int ret = MSP_SUCCESS;
            const char* login_params = "appid = 58249817, work_dir = .";

            const char* session_begin_params =
                "sub = iat, domain = iat, language = en_us, "
                "accent = mandarin, sample_rate = 16000, "
                "result_type = plain, result_encoding = utf8";

            ret = MSPLogin(NULL, NULL, login_params);
            if(MSP_SUCCESS != ret){
                MSPLogout();
                printf("MSPLogin failed , Error code %d.\n",ret);
            }

            printf("Demo recognizing the speech from microphone\n");
            printf("Speak in 10 seconds\n");
            sleep(2);
            demo_mic(session_begin_params);

            printf("10 sec passed\n");
        
            wakeupFlag=0;
            MSPLogout();
        }
        // 语音识别完成
        if(flag_ok){
            flag_ok=0;
            std_msgs::String msg;
            msg.data = g_result;
            pub_recognition_result.publish(msg);
        }
        if(flag_no){
            flag_no=0;
            std_msgs::String msg;
            msg.data = "failed";
            pub_recognition_result.publish(msg);
        }


        ros::spinOnce();
        loop_rate.sleep();
        count++;
    }

exit:
    MSPLogout(); // Logout...

    return 0;
}
