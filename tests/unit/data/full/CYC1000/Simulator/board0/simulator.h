#include <stdint.h>

#define NUM_JOINTS 1
#define NUM_HOMESWS 0
#define NUM_BITOUTS 2

extern uint8_t sim_running;

extern volatile int32_t joint_position[NUM_JOINTS];
extern volatile int32_t home_switch[NUM_HOMESWS];
extern volatile int32_t bitout_stat[NUM_BITOUTS];

#define NUM_JOINTS_X 1

#define NUM_JOINTS_X 1
extern int x_joints[NUM_JOINTS_X];

void* simThread(void* vargp);