
#include <stdio.h>
#include <unistd.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <time.h>
#include <riocore.h>

uint8_t rxBuffer[BUFFER_SIZE] = {0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0};
uint8_t txBuffer[BUFFER_SIZE] = {0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0};
float MULTIPLEXER_OUTPUT_VALUE;
uint8_t MULTIPLEXER_OUTPUT_ID;
uint8_t VAROUT1_WLED0_0_GREEN = 0;
uint8_t VAROUT1_WLED0_0_BLUE = 0;
uint8_t VAROUT1_WLED0_0_RED = 0;
uint8_t VAROUT1_WLED0_1_GREEN = 0;
uint8_t VAROUT1_WLED0_1_BLUE = 0;
uint8_t VAROUT1_WLED0_1_RED = 0;
uint8_t VAROUT1_WLED0_2_GREEN = 0;
uint8_t VAROUT1_WLED0_2_BLUE = 0;
uint8_t VAROUT1_WLED0_2_RED = 0;
uint8_t VARIN128_MODBUS0_RXDATA[16];
uint8_t VAROUT128_MODBUS0_TXDATA[16];
int16_t VARIN16_I2CBUS0_LM75_0_TEMP = 0;
uint8_t VARIN1_I2CBUS0_LM75_0_VALID = 0;
int32_t VAROUT32_STEPDIR0_VELOCITY = 0;
uint8_t VAROUT1_STEPDIR0_ENABLE = 0;
int32_t VARIN32_STEPDIR0_POSITION = 0;
int32_t VAROUT32_STEPDIR1_VELOCITY = 0;
uint8_t VAROUT1_STEPDIR1_ENABLE = 0;
int32_t VARIN32_STEPDIR1_POSITION = 0;
int32_t VAROUT32_STEPDIR2_VELOCITY = 0;
uint8_t VAROUT1_STEPDIR2_ENABLE = 0;
int32_t VARIN32_STEPDIR2_POSITION = 0;
uint8_t VARIN1_BITIN0_BIT = 0;
uint8_t VARIN1_BITIN1_BIT = 0;
uint8_t VARIN1_BITIN2_BIT = 0;


// PC -> MC
void read_rxbuffer(uint8_t *rxBuffer) {
    // memcpy(&header, &rxBuffer[0], 4) // 320;
    memcpy(&MULTIPLEXER_OUTPUT_VALUE, &rxBuffer[4], 2);
    memcpy(&MULTIPLEXER_OUTPUT_ID, &rxBuffer[6], 1);
    memcpy(&VAROUT128_MODBUS0_TXDATA, &rxBuffer[7], 16); // 264
    memcpy(&VAROUT32_STEPDIR0_VELOCITY, &rxBuffer[23], 4); // 136
    memcpy(&VAROUT32_STEPDIR1_VELOCITY, &rxBuffer[27], 4); // 104
    memcpy(&VAROUT32_STEPDIR2_VELOCITY, &rxBuffer[31], 4); // 72
    if ((rxBuffer[35] & (1<<7)) == 0) {
        VAROUT1_WLED0_0_GREEN = 0;
    } else {
        VAROUT1_WLED0_0_GREEN = 1;
    }
    if ((rxBuffer[35] & (1<<6)) == 0) {
        VAROUT1_WLED0_0_BLUE = 0;
    } else {
        VAROUT1_WLED0_0_BLUE = 1;
    }
    if ((rxBuffer[35] & (1<<5)) == 0) {
        VAROUT1_WLED0_0_RED = 0;
    } else {
        VAROUT1_WLED0_0_RED = 1;
    }
    if ((rxBuffer[35] & (1<<4)) == 0) {
        VAROUT1_WLED0_1_GREEN = 0;
    } else {
        VAROUT1_WLED0_1_GREEN = 1;
    }
    if ((rxBuffer[35] & (1<<3)) == 0) {
        VAROUT1_WLED0_1_BLUE = 0;
    } else {
        VAROUT1_WLED0_1_BLUE = 1;
    }
    if ((rxBuffer[35] & (1<<2)) == 0) {
        VAROUT1_WLED0_1_RED = 0;
    } else {
        VAROUT1_WLED0_1_RED = 1;
    }
    if ((rxBuffer[35] & (1<<1)) == 0) {
        VAROUT1_WLED0_2_GREEN = 0;
    } else {
        VAROUT1_WLED0_2_GREEN = 1;
    }
    if ((rxBuffer[35] & (1<<0)) == 0) {
        VAROUT1_WLED0_2_BLUE = 0;
    } else {
        VAROUT1_WLED0_2_BLUE = 1;
    }
    if ((rxBuffer[36] & (1<<7)) == 0) {
        VAROUT1_WLED0_2_RED = 0;
    } else {
        VAROUT1_WLED0_2_RED = 1;
    }
    if ((rxBuffer[36] & (1<<6)) == 0) {
        VAROUT1_STEPDIR0_ENABLE = 0;
    } else {
        VAROUT1_STEPDIR0_ENABLE = 1;
    }
    if ((rxBuffer[36] & (1<<5)) == 0) {
        VAROUT1_STEPDIR1_ENABLE = 0;
    } else {
        VAROUT1_STEPDIR1_ENABLE = 1;
    }
    if ((rxBuffer[36] & (1<<4)) == 0) {
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
    memcpy(&txBuffer[8], &MULTIPLEXER_OUTPUT_VALUE, 2); // 256
    memcpy(&txBuffer[10], &MULTIPLEXER_OUTPUT_ID, 1); // 240
    memcpy(&txBuffer[11], &VARIN128_MODBUS0_RXDATA, 16); // 232
    memcpy(&txBuffer[27], &VARIN32_STEPDIR0_POSITION, 4); // 104
    memcpy(&txBuffer[31], &VARIN32_STEPDIR1_POSITION, 4); // 72
    memcpy(&txBuffer[35], &VARIN32_STEPDIR2_POSITION, 4); // 40
    txBuffer[39] |= (VARIN1_BITIN0_BIT<<7); // 8
    txBuffer[39] |= (VARIN1_BITIN1_BIT<<6); // 7
    txBuffer[39] |= (VARIN1_BITIN2_BIT<<5); // 6

}
