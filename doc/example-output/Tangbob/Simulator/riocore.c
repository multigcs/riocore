
#include <stdio.h>
#include <unistd.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <time.h>
#include <riocore.h>

uint8_t rxBuffer[BUFFER_SIZE] = {0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0};
uint8_t txBuffer[BUFFER_SIZE] = {0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0};
float MULTIPLEXER_OUTPUT_VALUE;
uint8_t MULTIPLEXER_OUTPUT_ID;
uint8_t VAROUT1_WLED0_0_GREEN = 0;
uint8_t VAROUT1_WLED0_0_BLUE = 0;
uint8_t VAROUT1_WLED0_0_RED = 0;
uint8_t VARIN128_MODBUS0_RXDATA[16];
uint8_t VAROUT128_MODBUS0_TXDATA[16];
int16_t VARIN16_I2CBUS0_LM75_0_TEMP = 0;
uint8_t VARIN1_I2CBUS0_LM75_0_VALID = 0;
uint8_t VAROUT1_BITOUT0_BIT = 0;
uint8_t VARIN1_BITIN0_BIT = 0;
uint8_t VARIN1_BITIN1_BIT = 0;
uint8_t VARIN1_BITIN2_BIT = 0;
uint8_t VAROUT1_BITOUT1_BIT = 0;
int32_t VAROUT32_PWMOUT0_DTY = 0;
uint8_t VAROUT1_PWMOUT0_ENABLE = 0;
uint8_t VARIN1_BITIN3_BIT = 0;
uint8_t VARIN1_BITIN4_BIT = 0;
int32_t VAROUT32_STEPDIR0_VELOCITY = 0;
uint8_t VAROUT1_STEPDIR0_ENABLE = 0;
int32_t VARIN32_STEPDIR0_POSITION = 0;
int32_t VAROUT32_STEPDIR1_VELOCITY = 0;
uint8_t VAROUT1_STEPDIR1_ENABLE = 0;
int32_t VARIN32_STEPDIR1_POSITION = 0;
int32_t VAROUT32_STEPDIR2_VELOCITY = 0;
uint8_t VAROUT1_STEPDIR2_ENABLE = 0;
int32_t VARIN32_STEPDIR2_POSITION = 0;
int32_t VAROUT32_STEPDIR3_VELOCITY = 0;
uint8_t VAROUT1_STEPDIR3_ENABLE = 0;
int32_t VARIN32_STEPDIR3_POSITION = 0;


// PC -> MC
void read_rxbuffer(uint8_t *rxBuffer) {
    // memcpy(&header, &rxBuffer[0], 4) // 352;
    memcpy(&VAROUT128_MODBUS0_TXDATA, &rxBuffer[4], 16); // 320
    memcpy(&VAROUT32_PWMOUT0_DTY, &rxBuffer[20], 4); // 192
    memcpy(&VAROUT32_STEPDIR0_VELOCITY, &rxBuffer[24], 4); // 160
    memcpy(&VAROUT32_STEPDIR1_VELOCITY, &rxBuffer[28], 4); // 128
    memcpy(&VAROUT32_STEPDIR2_VELOCITY, &rxBuffer[32], 4); // 96
    memcpy(&VAROUT32_STEPDIR3_VELOCITY, &rxBuffer[36], 4); // 64
    if ((rxBuffer[40] & (1<<7)) == 0) {
        VAROUT1_WLED0_0_GREEN = 0;
    } else {
        VAROUT1_WLED0_0_GREEN = 1;
    }
    if ((rxBuffer[40] & (1<<6)) == 0) {
        VAROUT1_WLED0_0_BLUE = 0;
    } else {
        VAROUT1_WLED0_0_BLUE = 1;
    }
    if ((rxBuffer[40] & (1<<5)) == 0) {
        VAROUT1_WLED0_0_RED = 0;
    } else {
        VAROUT1_WLED0_0_RED = 1;
    }
    if ((rxBuffer[40] & (1<<4)) == 0) {
        VAROUT1_BITOUT0_BIT = 0;
    } else {
        VAROUT1_BITOUT0_BIT = 1;
    }
    if ((rxBuffer[40] & (1<<3)) == 0) {
        VAROUT1_BITOUT1_BIT = 0;
    } else {
        VAROUT1_BITOUT1_BIT = 1;
    }
    if ((rxBuffer[40] & (1<<2)) == 0) {
        VAROUT1_PWMOUT0_ENABLE = 0;
    } else {
        VAROUT1_PWMOUT0_ENABLE = 1;
    }
    if ((rxBuffer[40] & (1<<1)) == 0) {
        VAROUT1_STEPDIR0_ENABLE = 0;
    } else {
        VAROUT1_STEPDIR0_ENABLE = 1;
    }
    if ((rxBuffer[40] & (1<<0)) == 0) {
        VAROUT1_STEPDIR1_ENABLE = 0;
    } else {
        VAROUT1_STEPDIR1_ENABLE = 1;
    }
    if ((rxBuffer[41] & (1<<7)) == 0) {
        VAROUT1_STEPDIR2_ENABLE = 0;
    } else {
        VAROUT1_STEPDIR2_ENABLE = 1;
    }
    if ((rxBuffer[41] & (1<<6)) == 0) {
        VAROUT1_STEPDIR3_ENABLE = 0;
    } else {
        VAROUT1_STEPDIR3_ENABLE = 1;
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
    memcpy(&txBuffer[8], &MULTIPLEXER_OUTPUT_VALUE, 2); // 288
    memcpy(&txBuffer[10], &MULTIPLEXER_OUTPUT_ID, 1); // 272
    memcpy(&txBuffer[11], &VARIN128_MODBUS0_RXDATA, 16); // 264
    memcpy(&txBuffer[27], &VARIN32_STEPDIR0_POSITION, 4); // 136
    memcpy(&txBuffer[31], &VARIN32_STEPDIR1_POSITION, 4); // 104
    memcpy(&txBuffer[35], &VARIN32_STEPDIR2_POSITION, 4); // 72
    memcpy(&txBuffer[39], &VARIN32_STEPDIR3_POSITION, 4); // 40
    txBuffer[43] |= (VARIN1_BITIN0_BIT<<7); // 8
    txBuffer[43] |= (VARIN1_BITIN1_BIT<<6); // 7
    txBuffer[43] |= (VARIN1_BITIN2_BIT<<5); // 6
    txBuffer[43] |= (VARIN1_BITIN3_BIT<<4); // 5
    txBuffer[43] |= (VARIN1_BITIN4_BIT<<3); // 4

}
