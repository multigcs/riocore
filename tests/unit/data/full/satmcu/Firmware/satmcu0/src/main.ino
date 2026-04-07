
int rxPin = 1;
int txPin = 0;

#define MCU_BUFFER_SIZE_TX 22
#define MCU_BUFFER_SIZE_RX 5

uint8_t tx_buffer[MCU_BUFFER_SIZE_TX + 1] = {0x61, 0x74, 0x61, 0x64,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0};
uint8_t rx_buffer[MCU_BUFFER_SIZE_RX + 1] = {0, 0, 0, 0,  0, 0};

int32_t VARIN32_FEED_POSITION = 0;
int32_t VARIN32_SPINDLE_POSITION = 0;
int32_t VARIN32_RAPID_POSITION = 0;
int32_t VARIN32_JOGWHEEL_POSITION = 0;
bool VARIN1_MPGESTOP_BIT = 0;
bool VARIN1_SCALE0_BIT = 0;
bool VAROUT1_LEDSCALE0_BIT = 0;
bool VARIN1_SCALE1_BIT = 0;
bool VARIN1_SCALE2_BIT = 0;
bool VARIN1_SELECTX_BIT = 0;
bool VARIN1_SELECTY_BIT = 0;
bool VAROUT1_LEDSCALE1_BIT = 0;
bool VAROUT1_LEDSCALE2_BIT = 0;
bool VAROUT1_SELECTEDX_BIT = 0;
bool VAROUT1_SELECTEDY_BIT = 0;
bool VAROUT1_SELECTEDZ_BIT = 0;
bool VARIN1_SELECTZ_BIT = 0;
bool VARIN1_LBUTTON_BIT = 0;
bool VARIN1_CBUTTON_BIT = 0;
bool VARIN1_RBUTTON_BIT = 0;

void rio_rtx(void) {
    uint8_t received_ok = 0;
    // receive rx_buffer
    int flen = Serial1.readBytes(rx_buffer, MCU_BUFFER_SIZE_RX + 1);
    if (flen == MCU_BUFFER_SIZE_RX + 1 && rx_buffer[0] == 0x74 && rx_buffer[1] == 0x69 && rx_buffer[2] == 0x72 && rx_buffer[3] == 0x77) {
        uint8_t rx_csum = 0;
        for (int i = 0; i < MCU_BUFFER_SIZE_RX; i++) {
            rx_csum += rx_buffer[i];
        }
        if (rx_buffer[MCU_BUFFER_SIZE_RX] == rx_csum) {
            // read rx_buffer
            if ((rx_buffer[4] & (1<<7)) != 0) {
                VAROUT1_LEDSCALE0_BIT = 1;
            } else {
                VAROUT1_LEDSCALE0_BIT = 0;
            }
            if ((rx_buffer[4] & (1<<6)) != 0) {
                VAROUT1_LEDSCALE1_BIT = 1;
            } else {
                VAROUT1_LEDSCALE1_BIT = 0;
            }
            if ((rx_buffer[4] & (1<<5)) != 0) {
                VAROUT1_LEDSCALE2_BIT = 1;
            } else {
                VAROUT1_LEDSCALE2_BIT = 0;
            }
            if ((rx_buffer[4] & (1<<4)) != 0) {
                VAROUT1_SELECTEDX_BIT = 1;
            } else {
                VAROUT1_SELECTEDX_BIT = 0;
            }
            if ((rx_buffer[4] & (1<<3)) != 0) {
                VAROUT1_SELECTEDY_BIT = 1;
            } else {
                VAROUT1_SELECTEDY_BIT = 0;
            }
            if ((rx_buffer[4] & (1<<2)) != 0) {
                VAROUT1_SELECTEDZ_BIT = 1;
            } else {
                VAROUT1_SELECTEDZ_BIT = 0;
            }
            received_ok = 1;
        }
    }
    if (received_ok == 1) {
        // write tx_buffer
        memcpy(tx_buffer + 4, &VARIN32_FEED_POSITION, 4);
        memcpy(tx_buffer + 8, &VARIN32_SPINDLE_POSITION, 4);
        memcpy(tx_buffer + 12, &VARIN32_RAPID_POSITION, 4);
        memcpy(tx_buffer + 16, &VARIN32_JOGWHEEL_POSITION, 4);
        if (VARIN1_MPGESTOP_BIT == 1) {
            tx_buffer[20] |= (1<<7);
        } else {
            tx_buffer[20] &= ~(1<<7);
        }
        if (VARIN1_SCALE0_BIT == 1) {
            tx_buffer[20] |= (1<<6);
        } else {
            tx_buffer[20] &= ~(1<<6);
        }
        if (VARIN1_SCALE1_BIT == 1) {
            tx_buffer[20] |= (1<<5);
        } else {
            tx_buffer[20] &= ~(1<<5);
        }
        if (VARIN1_SCALE2_BIT == 1) {
            tx_buffer[20] |= (1<<4);
        } else {
            tx_buffer[20] &= ~(1<<4);
        }
        if (VARIN1_SELECTX_BIT == 1) {
            tx_buffer[20] |= (1<<3);
        } else {
            tx_buffer[20] &= ~(1<<3);
        }
        if (VARIN1_SELECTY_BIT == 1) {
            tx_buffer[20] |= (1<<2);
        } else {
            tx_buffer[20] &= ~(1<<2);
        }
        if (VARIN1_SELECTZ_BIT == 1) {
            tx_buffer[20] |= (1<<1);
        } else {
            tx_buffer[20] &= ~(1<<1);
        }
        if (VARIN1_LBUTTON_BIT == 1) {
            tx_buffer[20] |= (1<<0);
        } else {
            tx_buffer[20] &= ~(1<<0);
        }
        if (VARIN1_CBUTTON_BIT == 1) {
            tx_buffer[21] |= (1<<7);
        } else {
            tx_buffer[21] &= ~(1<<7);
        }
        if (VARIN1_RBUTTON_BIT == 1) {
            tx_buffer[21] |= (1<<6);
        } else {
            tx_buffer[21] &= ~(1<<6);
        }

        // send tx_buffer
        uint8_t csum = 0;
        for (int i = 0; i < MCU_BUFFER_SIZE_TX; i++) {
            csum += tx_buffer[i];
        }
        tx_buffer[MCU_BUFFER_SIZE_TX] = csum;
        Serial1.write(tx_buffer, MCU_BUFFER_SIZE_TX + 1);
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


#define FEED_PIN_A 14
#define FEED_PIN_B 15
#define SPINDLE_PIN_A 2
#define SPINDLE_PIN_B 3
#define RAPID_PIN_A 5
#define RAPID_PIN_B 4
#define JOGWHEEL_PIN_A 12
#define JOGWHEEL_PIN_B 13
#define MPGESTOP_PIN_BIT 16
#define SCALE0_PIN_BIT 11
#define LEDSCALE0_PIN_BIT 10
#define SCALE1_PIN_BIT 9
#define SCALE2_PIN_BIT 7
#define SELECTX_PIN_BIT 18
#define SELECTY_PIN_BIT 20
#define LEDSCALE1_PIN_BIT 8
#define LEDSCALE2_PIN_BIT 6
#define SELECTEDX_PIN_BIT 19
#define SELECTEDY_PIN_BIT 21
#define SELECTEDZ_PIN_BIT 27
#define SELECTZ_PIN_BIT 26
#define LBUTTON_PIN_BIT 17
#define CBUTTON_PIN_BIT 22
#define RBUTTON_PIN_BIT 28

void setup() {
    encoder[0].begin(FEED_PIN_A, FEED_PIN_B, 4);
    encoder[1].begin(SPINDLE_PIN_A, SPINDLE_PIN_B, 4);
    encoder[2].begin(RAPID_PIN_A, RAPID_PIN_B, 4);
    encoder[3].begin(JOGWHEEL_PIN_A, JOGWHEEL_PIN_B, 4);

    pinMode(MPGESTOP_PIN_BIT, INPUT_PULLUP);
    pinMode(SCALE0_PIN_BIT, INPUT_PULLUP);
    pinMode(LEDSCALE0_PIN_BIT, OUTPUT);
    pinMode(SCALE1_PIN_BIT, INPUT_PULLUP);
    pinMode(SCALE2_PIN_BIT, INPUT_PULLUP);
    pinMode(SELECTX_PIN_BIT, INPUT_PULLUP);
    pinMode(SELECTY_PIN_BIT, INPUT_PULLUP);
    pinMode(LEDSCALE1_PIN_BIT, OUTPUT);
    pinMode(LEDSCALE2_PIN_BIT, OUTPUT);
    pinMode(SELECTEDX_PIN_BIT, OUTPUT);
    pinMode(SELECTEDY_PIN_BIT, OUTPUT);
    pinMode(SELECTEDZ_PIN_BIT, OUTPUT);
    pinMode(SELECTZ_PIN_BIT, INPUT_PULLUP);
    pinMode(LBUTTON_PIN_BIT, INPUT_PULLUP);
    pinMode(CBUTTON_PIN_BIT, INPUT_PULLUP);
    pinMode(RBUTTON_PIN_BIT, INPUT_PULLUP);
    Serial.begin(115200);
    Serial.setTimeout(10);
    Serial1.begin(1000000);
    Serial1.setTimeout(1);
    delay(100);
}

void loop() {
    for (int i = 0; i < NUM_ENCODERS; i++) {
        encoder[i].loop();
    }

    VARIN32_FEED_POSITION = encoder[0].getPosition();
    VARIN32_SPINDLE_POSITION = encoder[1].getPosition();
    VARIN32_RAPID_POSITION = encoder[2].getPosition();
    VARIN32_JOGWHEEL_POSITION = encoder[3].getPosition();

    VARIN1_MPGESTOP_BIT = 1 - digitalRead(MPGESTOP_PIN_BIT);
    VARIN1_SCALE0_BIT = 1 - digitalRead(SCALE0_PIN_BIT);
    VARIN1_SCALE1_BIT = 1 - digitalRead(SCALE1_PIN_BIT);
    VARIN1_SCALE2_BIT = 1 - digitalRead(SCALE2_PIN_BIT);
    VARIN1_SELECTX_BIT = 1 - digitalRead(SELECTX_PIN_BIT);
    VARIN1_SELECTY_BIT = 1 - digitalRead(SELECTY_PIN_BIT);
    VARIN1_SELECTZ_BIT = 1 - digitalRead(SELECTZ_PIN_BIT);
    VARIN1_LBUTTON_BIT = 1 - digitalRead(LBUTTON_PIN_BIT);
    VARIN1_CBUTTON_BIT = 1 - digitalRead(CBUTTON_PIN_BIT);
    VARIN1_RBUTTON_BIT = 1 - digitalRead(RBUTTON_PIN_BIT);
    rio_rtx();
    digitalWrite(LEDSCALE0_PIN_BIT, 1 - VAROUT1_LEDSCALE0_BIT);
    digitalWrite(LEDSCALE1_PIN_BIT, 1 - VAROUT1_LEDSCALE1_BIT);
    digitalWrite(LEDSCALE2_PIN_BIT, 1 - VAROUT1_LEDSCALE2_BIT);
    digitalWrite(SELECTEDX_PIN_BIT, 1 - VAROUT1_SELECTEDX_BIT);
    digitalWrite(SELECTEDY_PIN_BIT, 1 - VAROUT1_SELECTEDY_BIT);
    digitalWrite(SELECTEDZ_PIN_BIT, 1 - VAROUT1_SELECTEDZ_BIT);
}
