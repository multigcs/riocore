
int rxPin = 1;
int txPin = 0;

#define MCU_BUFFER_SIZE_TX 21
#define MCU_BUFFER_SIZE_RX 6

uint8_t tx_buffer[MCU_BUFFER_SIZE_TX + 2] = {0x64, 0x61, 0x74, 0x61,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0};
uint8_t rx_buffer[MCU_BUFFER_SIZE_RX + 2] = {0, 0, 0, 0,  0, 0, 0, 0};

int32_t VARIN32_ENCODER0_POSITION = 0;
int32_t VARIN32_ENCODER1_POSITION = 0;
int32_t VARIN32_ENCODER2_POSITION = 0;
int32_t VARIN32_ENCODER3_POSITION = 0;
bool VAROUT1_GPIOOUT0_BIT = 0;
bool VAROUT1_GPIOOUT1_BIT = 0;
bool VAROUT1_GPIOOUT2_BIT = 0;
bool VAROUT1_GPIOOUT3_BIT = 0;
bool VARIN1_GPIOIN0_BIT = 0;
bool VAROUT1_GPIOOUT4_BIT = 0;
bool VAROUT1_GPIOOUT5_BIT = 0;
bool VAROUT1_GPIOOUT6_BIT = 0;
bool VAROUT1_GPIOOUT7_BIT = 0;
bool VAROUT1_GPIOOUT8_BIT = 0;

void rio_rtx(void) {
    // write tx_buffer
    memcpy(tx_buffer + 4, &VARIN32_ENCODER0_POSITION, 4);
    memcpy(tx_buffer + 8, &VARIN32_ENCODER1_POSITION, 4);
    memcpy(tx_buffer + 12, &VARIN32_ENCODER2_POSITION, 4);
    memcpy(tx_buffer + 16, &VARIN32_ENCODER3_POSITION, 4);
    if (VARIN1_GPIOIN0_BIT == 1) {
        tx_buffer[20] |= (1<<7);
    } else {
        tx_buffer[20] &= ~(1<<7);
    }

    // send tx_buffer
    uint16_t csum = 0;
    for (int i = 0; i < MCU_BUFFER_SIZE_TX; i++) {
        csum += tx_buffer[i] + 1;
    }
    tx_buffer[MCU_BUFFER_SIZE_TX] = (csum >> 8 & 0xFF);
    tx_buffer[MCU_BUFFER_SIZE_TX + 1] = (csum & 0xFF);
    Serial1.write(tx_buffer, MCU_BUFFER_SIZE_TX + 2);

    // receive rx_buffer
    int flen = Serial1.readBytes(rx_buffer, MCU_BUFFER_SIZE_RX + 2);
    if (flen == MCU_BUFFER_SIZE_RX + 2) {
        uint16_t rx_csum = 0;
        for (int i = 0; i < MCU_BUFFER_SIZE_RX; i++) {
            rx_csum += rx_buffer[i] + 1;
        }
        if (rx_buffer[MCU_BUFFER_SIZE_RX] == (rx_csum >> 8 & 0xFF) && rx_buffer[MCU_BUFFER_SIZE_RX + 1] == (rx_csum & 0xFF)) {
            // read rx_buffer
            if ((rx_buffer[4] & (1<<7)) != 0) {
                VAROUT1_GPIOOUT0_BIT = 1;
            } else {
                VAROUT1_GPIOOUT0_BIT = 0;
            }
            if ((rx_buffer[4] & (1<<6)) != 0) {
                VAROUT1_GPIOOUT1_BIT = 1;
            } else {
                VAROUT1_GPIOOUT1_BIT = 0;
            }
            if ((rx_buffer[4] & (1<<5)) != 0) {
                VAROUT1_GPIOOUT2_BIT = 1;
            } else {
                VAROUT1_GPIOOUT2_BIT = 0;
            }
            if ((rx_buffer[4] & (1<<4)) != 0) {
                VAROUT1_GPIOOUT3_BIT = 1;
            } else {
                VAROUT1_GPIOOUT3_BIT = 0;
            }
            if ((rx_buffer[4] & (1<<3)) != 0) {
                VAROUT1_GPIOOUT4_BIT = 1;
            } else {
                VAROUT1_GPIOOUT4_BIT = 0;
            }
            if ((rx_buffer[4] & (1<<2)) != 0) {
                VAROUT1_GPIOOUT5_BIT = 1;
            } else {
                VAROUT1_GPIOOUT5_BIT = 0;
            }
            if ((rx_buffer[4] & (1<<1)) != 0) {
                VAROUT1_GPIOOUT6_BIT = 1;
            } else {
                VAROUT1_GPIOOUT6_BIT = 0;
            }
            if ((rx_buffer[4] & (1<<0)) != 0) {
                VAROUT1_GPIOOUT7_BIT = 1;
            } else {
                VAROUT1_GPIOOUT7_BIT = 0;
            }
            if ((rx_buffer[5] & (1<<7)) != 0) {
                VAROUT1_GPIOOUT8_BIT = 1;
            } else {
                VAROUT1_GPIOOUT8_BIT = 0;
            }
        }
    }
}


#include <ESPRotary.h>
#define NUM_ENCODERS 4

ESPRotary encoder[NUM_ENCODERS];

/*
hw_timer_t *timer = NULL;

void IRAM_ATTR handleLoop() {
    for (int i = 0; i < NUM_ENCODERS; i++) {
        encoder[i].loop();
    }
}
*/


#define VARIN32_ENCODER0_POSITION_PIN_A IO:36
#define VARIN32_ENCODER0_POSITION_PIN_B IO:39
#define VARIN32_ENCODER1_POSITION_PIN_A IO:34
#define VARIN32_ENCODER1_POSITION_PIN_B IO:35
#define VARIN32_ENCODER2_POSITION_PIN_A IO:32
#define VARIN32_ENCODER2_POSITION_PIN_B IO:33
#define VARIN32_ENCODER3_POSITION_PIN_A IO:25
#define VARIN32_ENCODER3_POSITION_PIN_B 26

void setup() {
    encoder[0].begin(VARIN32_ENCODER0_POSITION_PIN_A, VARIN32_ENCODER0_POSITION_PIN_B, 4);
    encoder[1].begin(VARIN32_ENCODER1_POSITION_PIN_A, VARIN32_ENCODER1_POSITION_PIN_B, 4);
    encoder[2].begin(VARIN32_ENCODER2_POSITION_PIN_A, VARIN32_ENCODER2_POSITION_PIN_B, 4);
    encoder[3].begin(VARIN32_ENCODER3_POSITION_PIN_A, VARIN32_ENCODER3_POSITION_PIN_B, 4);

    Serial.begin(115200);
    Serial.setTimeout(10);
    Serial1.begin(1000000);
    Serial1.setTimeout(1);
    delay(100);
}

void loop() {
    rio_rtx();
    for (int i = 0; i < NUM_ENCODERS; i++) {
        encoder[i].loop();
    }

    VARIN32_ENCODER0_POSITION = encoder[0].getPosition();
    VARIN32_ENCODER1_POSITION = encoder[1].getPosition();
    VARIN32_ENCODER2_POSITION = encoder[2].getPosition();
    VARIN32_ENCODER3_POSITION = encoder[3].getPosition();

}
