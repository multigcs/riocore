
#include <stdio.h>
#include <unistd.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <time.h>
#include <riocore.h>

uint8_t rxBuffer[BUFFER_SIZE] = {0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0};
uint8_t txBuffer[BUFFER_SIZE] = {0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0};
uint8_t VAROUT1_BITOUT0_BIT = 0;
uint8_t VARIN1_BITIN0_BIT = 0;
uint8_t VARIN1_BITIN1_BIT = 0;
int32_t VAROUT32_STEPDIR0_VELOCITY = 0;
uint8_t VAROUT1_STEPDIR0_ENABLE = 0;
int32_t VARIN32_STEPDIR0_POSITION = 0;
int32_t VAROUT32_STEPDIR1_VELOCITY = 0;
uint8_t VAROUT1_STEPDIR1_ENABLE = 0;
int32_t VARIN32_STEPDIR1_POSITION = 0;
int32_t VAROUT32_STEPDIR2_VELOCITY = 0;
uint8_t VAROUT1_STEPDIR2_ENABLE = 0;
int32_t VARIN32_STEPDIR2_POSITION = 0;


// PC -> MC
void read_rxbuffer(uint8_t *rxBuffer) {
    // memcpy(&header, &rxBuffer[0], 4) // 168;
    memcpy(&VAROUT32_STEPDIR0_VELOCITY, &rxBuffer[4], 4); // 136
    memcpy(&VAROUT32_STEPDIR1_VELOCITY, &rxBuffer[8], 4); // 104
    memcpy(&VAROUT32_STEPDIR2_VELOCITY, &rxBuffer[12], 4); // 72
    if ((rxBuffer[16] & (1<<7)) == 0) {
        VAROUT1_BITOUT0_BIT = 0;
    } else {
        VAROUT1_BITOUT0_BIT = 1;
    }
    if ((rxBuffer[16] & (1<<6)) == 0) {
        VAROUT1_STEPDIR0_ENABLE = 0;
    } else {
        VAROUT1_STEPDIR0_ENABLE = 1;
    }
    if ((rxBuffer[16] & (1<<5)) == 0) {
        VAROUT1_STEPDIR1_ENABLE = 0;
    } else {
        VAROUT1_STEPDIR1_ENABLE = 1;
    }
    if ((rxBuffer[16] & (1<<4)) == 0) {
        VAROUT1_STEPDIR2_ENABLE = 0;
    } else {
        VAROUT1_STEPDIR2_ENABLE = 1;
    }
}

// MC -> PC
void write_txbuffer(uint8_t *txBuffer) {
    int n = 0;
    for (n = 0; n < BUFFER_SIZE; n++) {
        txBuffer[n] = 0;
    }
    txBuffer[0] = 97;
    txBuffer[1] = 116;
    txBuffer[2] = 97;
    txBuffer[3] = 100;
    memcpy(&txBuffer[8], &VARIN32_STEPDIR0_POSITION, 4); // 104
    memcpy(&txBuffer[12], &VARIN32_STEPDIR1_POSITION, 4); // 72
    memcpy(&txBuffer[16], &VARIN32_STEPDIR2_POSITION, 4); // 40
    txBuffer[20] |= (VARIN1_BITIN0_BIT<<7); // 8
    txBuffer[20] |= (VARIN1_BITIN1_BIT<<6); // 7

}
