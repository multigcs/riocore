#include <stdio.h>
#include <unistd.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <time.h>

#define CLOCK_SPEED 48000000
#define BUFFER_SIZE 13 // 104 bits
#define UDP_IP "192.168.11.194"
#define SRC_PORT 2390
#define DST_PORT 2391

void read_rxbuffer(uint8_t *rxBuffer);
void write_txbuffer(uint8_t *txBuffer);

extern uint8_t rxBuffer[BUFFER_SIZE];
extern uint8_t txBuffer[BUFFER_SIZE];
extern uint8_t VARIN1_BITIN0_BIT;
extern uint8_t VAROUT1_BITOUT0_BIT;
extern uint8_t VAROUT1_BITOUT1_BIT;
extern int32_t VAROUT32_PWMOUT0_DTY;
extern uint8_t VAROUT1_PWMOUT0_ENABLE;
extern int32_t VAROUT32_STEPDIR0_VELOCITY;
extern uint8_t VAROUT1_STEPDIR0_ENABLE;
extern int32_t VARIN32_STEPDIR0_POSITION;
