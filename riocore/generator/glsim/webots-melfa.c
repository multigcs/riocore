#include <webots/robot.h>
#include <webots/motor.h>
#include <math.h>

#include <stdlib.h>
#include <simulator.h>

#define TIME_STEP 32

int glsim_run(int argc, char** argv) {
    uint8_t joint_n = 0;
    WbDeviceTag motor[6];

    wb_robot_init();
    motor[0] = wb_robot_get_device("A motor");
    motor[1] = wb_robot_get_device("B motor");
    motor[2] = wb_robot_get_device("C motor");
    motor[3] = wb_robot_get_device("D motor");
    motor[4] = wb_robot_get_device("E motor");
    motor[5] = wb_robot_get_device("F motor");

    while (wb_robot_step(TIME_STEP) != -1) {
        for (joint_n = 0; joint_n < 6; joint_n++) {
            float pos = joint_position[joint_n] / 100.0 / 180.0 * M_PI;
            if (joint_n == 1) {
                pos += M_PI / 2;
            }
            wb_motor_set_position(motor[joint_n], pos);
        }
    }

    wb_robot_cleanup();
    return 0;

}

