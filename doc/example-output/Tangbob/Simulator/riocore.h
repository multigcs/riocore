#include <stdio.h>
#include <unistd.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <time.h>

#define CLOCK_SPEED 27000000
#define BUFFER_SIZE 44 // 352 bits
#define UDP_IP "192.168.10.194"
#define SRC_PORT 2390
#define DST_PORT 2391

void read_rxbuffer(uint8_t *rxBuffer);
void write_txbuffer(uint8_t *txBuffer);

extern uint8_t rxBuffer[BUFFER_SIZE];
extern uint8_t txBuffer[BUFFER_SIZE];
extern float MULTIPLEXER_INPUT_VALUE;
extern uint8_t MULTIPLEXER_INPUT_ID;
extern uint8_t VAROUT1_WLED0_0_GREEN;
extern uint8_t VAROUT1_WLED0_0_BLUE;
extern uint8_t VAROUT1_WLED0_0_RED;
extern uint8_t VARIN128_MODBUS0_RXDATA[16];
extern uint8_t VAROUT128_MODBUS0_TXDATA[16];
extern int16_t VARIN16_I2CBUS0_LM75_0_TEMP;
extern uint8_t VARIN1_I2CBUS0_LM75_0_VALID;
extern uint8_t VAROUT1_BITOUT0_BIT;
extern uint8_t VARIN1_BITIN0_BIT;
extern uint8_t VARIN1_BITIN1_BIT;
extern uint8_t VARIN1_BITIN2_BIT;
extern uint8_t VAROUT1_BITOUT1_BIT;
extern int32_t VAROUT32_PWMOUT0_DTY;
extern uint8_t VAROUT1_PWMOUT0_ENABLE;
extern uint8_t VARIN1_BITIN3_BIT;
extern uint8_t VARIN1_BITIN4_BIT;
extern int32_t VAROUT32_STEPDIR0_VELOCITY;
extern uint8_t VAROUT1_STEPDIR0_ENABLE;
extern int32_t VARIN32_STEPDIR0_POSITION;
extern int32_t VAROUT32_STEPDIR1_VELOCITY;
extern uint8_t VAROUT1_STEPDIR1_ENABLE;
extern int32_t VARIN32_STEPDIR1_POSITION;
extern int32_t VAROUT32_STEPDIR2_VELOCITY;
extern uint8_t VAROUT1_STEPDIR2_ENABLE;
extern int32_t VARIN32_STEPDIR2_POSITION;
extern int32_t VAROUT32_STEPDIR3_VELOCITY;
extern uint8_t VAROUT1_STEPDIR3_ENABLE;
extern int32_t VARIN32_STEPDIR3_POSITION;
