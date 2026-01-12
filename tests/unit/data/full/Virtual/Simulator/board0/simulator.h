#include <stdint.h>

#define NUM_JOINTS 3
#define NUM_HOMESWS 0
#define NUM_BITOUTS 0

// Virtual size (in mm / scale = steps/mm)
#define VIRT_SCALE_X  joint_scales[0]
#define VIRT_SCALE_Y  joint_scales[1]
#define VIRT_SCALE_Z  joint_scales[2]
#define VIRT_WIDTH    1500.0
#define VIRT_HEIGHT   1500.0
#define VIRT_DEPTH    1500.0

extern uint8_t sim_running;

extern volatile int32_t joint_position[NUM_JOINTS];
extern volatile int32_t home_switch[NUM_HOMESWS];
extern volatile int32_t bitout_stat[NUM_BITOUTS];

#define NUM_JOINTS_X 1
#define NUM_JOINTS_Y 1
#define NUM_JOINTS_Z 1

#define NUM_JOINTS_X 1
extern int x_joints[NUM_JOINTS_X];
#define NUM_JOINTS_Y 1
extern int y_joints[NUM_JOINTS_Y];
#define NUM_JOINTS_Z 1
extern int z_joints[NUM_JOINTS_Z];

extern float joint_scales[NUM_JOINTS];

void* simThread(void* vargp);