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

int interface_init() {
    spi_init();
}

void interface_exit(void) {
    spi_exit();
}

void simulation(void) {
    float newpos = 0.0;
    if (VAROUT1_STEPDIR0_ENABLE == 1 && VAROUT32_STEPDIR0_VELOCITY != 0) {
        newpos = ((float)CLOCK_SPEED / (float)VAROUT32_STEPDIR0_VELOCITY / 2.0) / 1000.0 * 320.0 / 320.0;
        if ((int32_t)newpos == 0 && newpos > 0.0) {
            newpos = 1.0;
        } else if ((int32_t)newpos == 0 && newpos < 0.0) {
            newpos = -1.0;
        }
        printf(" # %f \n", newpos);
        VARIN32_STEPDIR0_POSITION += (int32_t)newpos;
    }
    joint_position[0] = VARIN32_STEPDIR0_POSITION;
    bitout_stat[0] = VAROUT1_BITOUT0_BIT;
    bitout_stat[1] = VAROUT1_BITOUT1_BIT;

    printf("\n\n");
    printf("> pwmout0.dty %i\n", VAROUT32_PWMOUT0_DTY);
    printf("> stepdir0.velocity %i\n", VAROUT32_STEPDIR0_VELOCITY);
    printf("> bitout0.bit %i\n", VAROUT1_BITOUT0_BIT);
    printf("> bitout1.bit %i\n", VAROUT1_BITOUT1_BIT);
    printf("> pwmout0.enable %i\n", VAROUT1_PWMOUT0_ENABLE);
    printf("> stepdir0.enable %i\n", VAROUT1_STEPDIR0_ENABLE);
    printf("\n");
    printf("< stepdir0.position %i\n", VARIN32_STEPDIR0_POSITION);
    printf("< bitin0.bit %i\n", VARIN1_BITIN0_BIT);
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
