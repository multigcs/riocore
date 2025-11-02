#include <stdint.h>

#define NUM_JOINTS 6
#define NUM_HOMESWS 0
#define NUM_BITOUTS 1

extern uint8_t sim_running;

extern volatile int32_t joint_position[NUM_JOINTS];
extern volatile int32_t home_switch[NUM_HOMESWS];
extern volatile int32_t bitout_stat[NUM_BITOUTS];

#define NUM_JOINTS_X 1
#define NUM_JOINTS_Y 1
#define NUM_JOINTS_Z 1
#define NUM_JOINTS_A 1
#define NUM_JOINTS_C 1
#define NUM_JOINTS_B 1

#define NUM_JOINTS_X 1
extern int x_joints[NUM_JOINTS_X];
#define NUM_JOINTS_Y 1
extern int y_joints[NUM_JOINTS_Y];
#define NUM_JOINTS_Z 1
extern int z_joints[NUM_JOINTS_Z];
#define NUM_JOINTS_A 1
extern int a_joints[NUM_JOINTS_A];
#define NUM_JOINTS_C 1
extern int c_joints[NUM_JOINTS_C];
#define NUM_JOINTS_B 1
extern int b_joints[NUM_JOINTS_B];

void* simThread(void* vargp);