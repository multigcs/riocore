
/***********************************************************************
*                       HELPER FUNCTIONS                               *
************************************************************************/

uint16_t crc16_update(uint16_t crc, uint8_t a) {
	int i;

	crc ^= (uint16_t)a;
	for (i = 0; i < 8; ++i) {
		if (crc & 1)
			crc = (crc >> 1) ^ 0xA001;
		else
			crc = (crc >> 1);
	}

	return crc;
}

void chatterCallback(const std_msgs::String::ConstPtr& msg) {
    ROS_INFO("I heard: [%s]", msg->data.c_str());
}

int main(int argc, char **argv) {

    data = (data_t*)malloc(sizeof(data_t));

    register_signals();
    interface_init();


    ros::init(argc, argv, "talker");
    ros::NodeHandle n;
    ros::NodeHandle n2;

    ros::Subscriber sub = n.subscribe("chatter", 1000, chatterCallback);
    ros::Publisher chatter_pub = n.advertise<std_msgs::String>("chatter", 1000);

    ros::Publisher chatter_pub2 = n.advertise<std_msgs::Float32>("chatter2", 1000);

    ros::Rate loop_rate(10);

    int count = 0;

    while (ros::ok()) {
        std_msgs::String msg;
        std::stringstream ss;
        ss << "hello world " << count;
        msg.data = ss.str();
        ROS_INFO("%s", msg.data.c_str());
        chatter_pub.publish(msg);

        //rio_readwrite();


        std_msgs::Float32 msg2;
        msg2.data = 123.0;
        chatter_pub2.publish(msg2);


        ros::spinOnce();
        loop_rate.sleep();
        ++count;
    }

    return 0;
}

/***********************************************************************/
