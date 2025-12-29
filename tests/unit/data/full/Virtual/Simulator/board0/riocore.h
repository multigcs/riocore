#include <stdio.h>
#include <unistd.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <time.h>

#define CLOCK_SPEED 27000000
#define BUFFER_SIZE_RX 20 // 160 bits
#define BUFFER_SIZE_TX 20 // 160 bits
#define UDP_IP "192.168.11.194"
#define SRC_PORT 2390
#define DST_PORT 2391

void read_rxbuffer(uint8_t *rxBuffer);
void write_txbuffer(uint8_t *txBuffer);

extern uint8_t rxBuffer[BUFFER_SIZE_RX];
extern uint8_t txBuffer[BUFFER_SIZE_TX];
extern uint8_t VAROUT1_BOARD0_WLED_0_GREEN;
extern uint8_t VAROUT1_BOARD0_WLED_0_BLUE;
extern uint8_t VAROUT1_BOARD0_WLED_0_RED;
extern int32_t VAROUT32_STEPDIR0_VELOCITY;
extern uint8_t VAROUT1_STEPDIR0_ENABLE;
extern int32_t VARIN32_STEPDIR0_POSITION;
extern int32_t VAROUT32_STEPDIR1_VELOCITY;
extern uint8_t VAROUT1_STEPDIR1_ENABLE;
extern int32_t VARIN32_STEPDIR1_POSITION;
extern int32_t VAROUT32_STEPDIR2_VELOCITY;
extern uint8_t VAROUT1_STEPDIR2_ENABLE;
extern int32_t VARIN32_STEPDIR2_POSITION;
