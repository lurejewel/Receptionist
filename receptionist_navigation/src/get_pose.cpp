/*
  改进：可以get任何多的点。
  我不确定有没有写好
*/
#include<ros/ros.h>
#include<std_msgs/String.h>
#include<geometry_msgs/PoseWithCovariance.h>
#include<geometry_msgs/PoseWithCovarianceStamped.h>
#include<iostream>
#include<fstream>
#include<string>
#include<cstdlib>
using namespace std;

//define a waypoint variable
vector<geometry_msgs::PoseWithCovariance> pose;
unsigned int num = 0;

void waypointscallback(const geometry_msgs::PoseWithCovarianceStamped::ConstPtr& msg)
{   
    pose.push_back(msg->pose);
    num++;
    cout<<"Waypoint "<<pose.size()<<" recevied!"<<endl;
}


int main(int argc, char** argv)
{
    //initialize the node named GetPose
    ros::init(argc, argv, "GetPose");
    ros::NodeHandle nh_;
    //define the waypoint subscriber
    ros::Subscriber waypoint_sub = nh_.subscribe("amcl_pose", 1, waypointscallback);

    unsigned int count = 0;

    //define the flags
    const string pose_flag = "get";
    const string end_flag = "stop";
    string input;

    cout<<"This program is used to get the four waypoints of the robot."<<endl;
    cout<<"Please input 'get' to get the waypoint."<<endl;
    cout<<"Please input 'stop' to end the waypoint getting."<<endl;

    while(getline(cin, input))
    {   
        //check the illegal input
        if(input != pose_flag && input != end_flag)
        {
            cout<<"Illegal input! Please input again."<<endl;
            continue;
        }

        //get the pose or end
        if(input == pose_flag)
        {
            cout<<"Get the waypoint "<<++count<<"."<<endl;
            ros::spinOnce();
        }else if(input == end_flag)
              {
                  cout<<"Get pose ended!"<<endl;
                  break;       
              }
    }

    //load the data into the position file
    //路径记得改
    ofstream posefile("/home/lurejewel/catkin_ws/src/Whereisthis/whereisthis_nav/waypoints.txt",ios::trunc|ios::out|ios::in);
    // printf("$(rospack find receptionist_navigation)/waypoints.txt");
    if(!posefile){  
        cerr<<"Open error!"<<endl;  
        // system("pause");
        exit(0);  
    }   
 
    for(int i = 0; i < pose.size(); i++)
    { 
        cout<<"i="<<i<<endl;
        posefile<<"The "<<(i+1)<<" waypoint :"<<endl;
        posefile<<"Position:"<<endl;
        posefile<<"  x = "<<pose[i].pose.position.x<<endl; 
        posefile<<"  y = "<<pose[i].pose.position.y<<endl;
        posefile<<"  z = "<<pose[i].pose.position.z<<endl;
        posefile<<"Orientation:"<<endl;
        posefile<<"  x = "<<pose[i].pose.orientation.x<<endl;
        posefile<<"  y = "<<pose[i].pose.orientation.y<<endl;
        posefile<<"  z = "<<pose[i].pose.orientation.z<<endl;
        posefile<<"  w = "<<pose[i].pose.orientation.w<<endl;
        posefile<<"--------------------------"<<endl;
    }
    
    posefile.close();  
    cout<<"Processing over! Please open the file and check!"<<endl; 
    // system("pause");

    return 0;    
}
