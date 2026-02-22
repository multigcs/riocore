
int rxPin = 18;
int txPin = 19;

#define MCU_BUFFER_SIZE_TX 21
#define MCU_BUFFER_SIZE_RX 6

uint8_t tx_buffer[MCU_BUFFER_SIZE_TX + 2] = {0x64, 0x61, 0x74, 0x61,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0};
uint8_t rx_buffer[MCU_BUFFER_SIZE_RX + 2] = {0, 0, 0, 0,  0, 0,  0, 0};

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
    Serial2.write(tx_buffer, MCU_BUFFER_SIZE_TX + 2);

    // receive rx_buffer
    int flen = Serial2.readBytes(rx_buffer, MCU_BUFFER_SIZE_RX + 2);
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
hw_timer_t *timer = NULL;

void IRAM_ATTR handleLoop() {
    for (int i = 0; i < NUM_ENCODERS; i++) {
        encoder[i].loop();
    }
}



#define VARIN32_ENCODER0_POSITION_PIN_A 36
#define VARIN32_ENCODER0_POSITION_PIN_B 39
#define VARIN32_ENCODER1_POSITION_PIN_A 34
#define VARIN32_ENCODER1_POSITION_PIN_B 35
#define VARIN32_ENCODER2_POSITION_PIN_A 32
#define VARIN32_ENCODER2_POSITION_PIN_B 33
#define VARIN32_ENCODER3_POSITION_PIN_A 25
#define VARIN32_ENCODER3_POSITION_PIN_B 26
#define VAROUT1_GPIOOUT0_BIT_PIN_BIT 23
#define VAROUT1_GPIOOUT1_BIT_PIN_BIT 22
#define VAROUT1_GPIOOUT2_BIT_PIN_BIT 21
#define VAROUT1_GPIOOUT3_BIT_PIN_BIT 5
#define VARIN1_GPIOIN0_BIT_PIN_BIT 0
#define VAROUT1_GPIOOUT4_BIT_PIN_BIT 17
#define VAROUT1_GPIOOUT5_BIT_PIN_BIT 16
#define VAROUT1_GPIOOUT6_BIT_PIN_BIT 4
#define VAROUT1_GPIOOUT7_BIT_PIN_BIT 2
#define VAROUT1_GPIOOUT8_BIT_PIN_BIT 15

void setup() {

    encoder[0].begin(VARIN32_ENCODER0_POSITION_PIN_A, VARIN32_ENCODER0_POSITION_PIN_B, 4);
    encoder[1].begin(VARIN32_ENCODER1_POSITION_PIN_A, VARIN32_ENCODER1_POSITION_PIN_B, 4);
    encoder[2].begin(VARIN32_ENCODER2_POSITION_PIN_A, VARIN32_ENCODER2_POSITION_PIN_B, 4);
    encoder[3].begin(VARIN32_ENCODER3_POSITION_PIN_A, VARIN32_ENCODER3_POSITION_PIN_B, 4);

    timer = timerBegin(0, 80, true);
    timerAttachInterrupt(timer, &handleLoop, true);
    timerAlarmWrite(timer, 100, true);
    timerAlarmEnable(timer);

    pinMode(VAROUT1_GPIOOUT0_BIT_PIN_BIT, OUTPUT);
    pinMode(VAROUT1_GPIOOUT1_BIT_PIN_BIT, OUTPUT);
    pinMode(VAROUT1_GPIOOUT2_BIT_PIN_BIT, OUTPUT);
    pinMode(VAROUT1_GPIOOUT3_BIT_PIN_BIT, OUTPUT);
    pinMode(VARIN1_GPIOIN0_BIT_PIN_BIT, INPUT_PULLUP);
    pinMode(VAROUT1_GPIOOUT4_BIT_PIN_BIT, OUTPUT);
    pinMode(VAROUT1_GPIOOUT5_BIT_PIN_BIT, OUTPUT);
    pinMode(VAROUT1_GPIOOUT6_BIT_PIN_BIT, OUTPUT);
    pinMode(VAROUT1_GPIOOUT7_BIT_PIN_BIT, OUTPUT);
    pinMode(VAROUT1_GPIOOUT8_BIT_PIN_BIT, OUTPUT);

    Serial.begin(115200);
    Serial.setTimeout(10);
    Serial2.begin(1000000, SERIAL_8N1, rxPin, txPin);
    Serial2.setTimeout(1);
    delay(100);
}

void loop() {


    VARIN1_GPIOIN0_BIT = digitalRead(VARIN1_GPIOIN0_BIT_PIN_BIT);

    rio_rtx();

    VARIN32_ENCODER0_POSITION = encoder[0].getPosition();
    VARIN32_ENCODER1_POSITION = encoder[1].getPosition();
    VARIN32_ENCODER2_POSITION = encoder[2].getPosition();
    VARIN32_ENCODER3_POSITION = encoder[3].getPosition();

    digitalWrite(VAROUT1_GPIOOUT0_BIT_PIN_BIT, VAROUT1_GPIOOUT0_BIT);
    digitalWrite(VAROUT1_GPIOOUT1_BIT_PIN_BIT, VAROUT1_GPIOOUT1_BIT);
    digitalWrite(VAROUT1_GPIOOUT2_BIT_PIN_BIT, VAROUT1_GPIOOUT2_BIT);
    digitalWrite(VAROUT1_GPIOOUT3_BIT_PIN_BIT, VAROUT1_GPIOOUT3_BIT);
    digitalWrite(VAROUT1_GPIOOUT4_BIT_PIN_BIT, VAROUT1_GPIOOUT4_BIT);
    digitalWrite(VAROUT1_GPIOOUT5_BIT_PIN_BIT, VAROUT1_GPIOOUT5_BIT);
    digitalWrite(VAROUT1_GPIOOUT6_BIT_PIN_BIT, VAROUT1_GPIOOUT6_BIT);
    digitalWrite(VAROUT1_GPIOOUT7_BIT_PIN_BIT, VAROUT1_GPIOOUT7_BIT);
    digitalWrite(VAROUT1_GPIOOUT8_BIT_PIN_BIT, VAROUT1_GPIOOUT8_BIT);

}
