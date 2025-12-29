#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <simulator.h>
#include <riocore.h>

uint8_t sim_running = 1;

int udp_init(const char *dstAddress, int dstPort, int srcPort);
void udp_tx(uint8_t *txBuffer, uint16_t size);
int udp_rx(uint8_t *rxBuffer, uint16_t size);
void udp_exit();

volatile int32_t joint_position[NUM_JOINTS];
volatile int32_t home_switch[NUM_HOMESWS];
volatile int32_t bitout_stat[NUM_BITOUTS];

int x_joints[NUM_JOINTS_X] = {0};
int y_joints[NUM_JOINTS_Y] = {1};
int z_joints[NUM_JOINTS_Z] = {2};

int interface_init() {
    udp_init("0.0.0.0", DST_PORT, SRC_PORT);
}

void interface_exit(void) {
    udp_exit();
}

void simulation(void) {
    float newpos = 0.0;
    if (VAROUT1_STEPDIR0_ENABLE == 1 && VAROUT32_STEPDIR0_VELOCITY != 0) {
        newpos = ((float)CLOCK_SPEED / (float)VAROUT32_STEPDIR0_VELOCITY / 2.0) / 1000.0 * -800.0 / -800.0;
        if ((int32_t)newpos == 0 && newpos > 0.0) {
            newpos = 1.0;
        } else if ((int32_t)newpos == 0 && newpos < 0.0) {
            newpos = -1.0;
        }
        printf(" # %f \n", newpos);
        VARIN32_STEPDIR0_POSITION += (int32_t)newpos;
    }
    joint_position[0] = VARIN32_STEPDIR0_POSITION;
    if (VAROUT1_STEPDIR1_ENABLE == 1 && VAROUT32_STEPDIR1_VELOCITY != 0) {
        newpos = ((float)CLOCK_SPEED / (float)VAROUT32_STEPDIR1_VELOCITY / 2.0) / 1000.0 * 800.0 / 800.0;
        if ((int32_t)newpos == 0 && newpos > 0.0) {
            newpos = 1.0;
        } else if ((int32_t)newpos == 0 && newpos < 0.0) {
            newpos = -1.0;
        }
        printf(" # %f \n", newpos);
        VARIN32_STEPDIR1_POSITION += (int32_t)newpos;
    }
    joint_position[1] = VARIN32_STEPDIR1_POSITION;
    if (VAROUT1_STEPDIR2_ENABLE == 1 && VAROUT32_STEPDIR2_VELOCITY != 0) {
        newpos = ((float)CLOCK_SPEED / (float)VAROUT32_STEPDIR2_VELOCITY / 2.0) / 1000.0 * -1600.0 / -1600.0;
        if ((int32_t)newpos == 0 && newpos > 0.0) {
            newpos = 1.0;
        } else if ((int32_t)newpos == 0 && newpos < 0.0) {
            newpos = -1.0;
        }
        printf(" # %f \n", newpos);
        VARIN32_STEPDIR2_POSITION += (int32_t)newpos;
    }
    joint_position[2] = VARIN32_STEPDIR2_POSITION;
    if (joint_position[0] < 0.0) {
        VARIN1_BITIN0_BIT = 1;
    } else {
        VARIN1_BITIN0_BIT = 0;
    }
    home_switch[0] = VARIN1_BITIN0_BIT;
    if (joint_position[1] < 0.0) {
        VARIN1_BITIN1_BIT = 1;
    } else {
        VARIN1_BITIN1_BIT = 0;
    }
    home_switch[1] = VARIN1_BITIN1_BIT;
    if (joint_position[2] > 2000.0) {
        VARIN1_BITIN2_BIT = 1;
    } else {
        VARIN1_BITIN2_BIT = 0;
    }
    home_switch[2] = VARIN1_BITIN2_BIT;
    bitout_stat[0] = VAROUT1_BITOUT0_BIT;

    printf("\n\n");
    printf("> stepdir0.velocity %i\n", VAROUT32_STEPDIR0_VELOCITY);
    printf("> stepdir1.velocity %i\n", VAROUT32_STEPDIR1_VELOCITY);
    printf("> stepdir2.velocity %i\n", VAROUT32_STEPDIR2_VELOCITY);
    printf("> stepdir0.enable %i\n", VAROUT1_STEPDIR0_ENABLE);
    printf("> stepdir1.enable %i\n", VAROUT1_STEPDIR1_ENABLE);
    printf("> stepdir2.enable %i\n", VAROUT1_STEPDIR2_ENABLE);
    printf("> fpga0_wled.0_green %i\n", VAROUT1_FPGA0_WLED_0_GREEN);
    printf("> fpga0_wled.0_blue %i\n", VAROUT1_FPGA0_WLED_0_BLUE);
    printf("> fpga0_wled.0_red %i\n", VAROUT1_FPGA0_WLED_0_RED);
    printf("> bitout0.bit %i\n", VAROUT1_BITOUT0_BIT);
    printf("\n");
    printf("< stepdir0.position %i\n", VARIN32_STEPDIR0_POSITION);
    printf("< stepdir1.position %i\n", VARIN32_STEPDIR1_POSITION);
    printf("< stepdir2.position %i\n", VARIN32_STEPDIR2_POSITION);
    printf("< i2cbus0.lm75_0_temp %i\n", VARIN16_I2CBUS0_LM75_0_TEMP);
    printf("< i2cbus0.lm75_0_valid %i\n", VARIN1_I2CBUS0_LM75_0_VALID);
    printf("< bitin0.bit %i\n", VARIN1_BITIN0_BIT);
    printf("< bitin1.bit %i\n", VARIN1_BITIN1_BIT);
    printf("< bitin2.bit %i\n", VARIN1_BITIN2_BIT);
}

void* simThread(void* vargp) {
    uint16_t ret = 0;

    interface_init(0, NULL);

    while (sim_running) {
        ret = udp_rx(rxBuffer, BUFFER_SIZE_RX);
        if (ret == BUFFER_SIZE_RX && rxBuffer[0] == 0x74 && rxBuffer[1] == 0x69 && rxBuffer[2] == 0x72 && rxBuffer[3] == 0x77) {
            read_rxbuffer(rxBuffer);
            write_txbuffer(txBuffer);
            udp_tx(txBuffer, BUFFER_SIZE_TX);

            simulation();
        }
    }
    return NULL;
}
