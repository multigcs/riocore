
int rxPin = 2;
int txPin = 1;

#define MCU_BUFFER_SIZE_TX 5
#define MCU_BUFFER_SIZE_RX 5

uint8_t tx_buffer[MCU_BUFFER_SIZE_TX + 2] = {0x64, 0x61, 0x74, 0x61,  0,  0, 0};
uint8_t rx_buffer[MCU_BUFFER_SIZE_RX + 2] = {0, 0, 0, 0,  0,  0, 0};

bool VAROUT1_GPIOOUT9_BIT = 0;
bool VARIN1_GPIOIN1_BIT = 0;

void rio_rtx(void) {
    // write tx_buffer
    if (VARIN1_GPIOIN1_BIT == 1) {
        tx_buffer[4] |= (1<<7);
    } else {
        tx_buffer[4] &= ~(1<<7);
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
                VAROUT1_GPIOOUT9_BIT = 1;
            } else {
                VAROUT1_GPIOOUT9_BIT = 0;
            }
        }
    }
}


#define VAROUT1_GPIOOUT9_BIT_PIN_BIT 14
#define VARIN1_GPIOIN1_BIT_PIN_BIT 15

void setup() {


    pinMode(VAROUT1_GPIOOUT9_BIT_PIN_BIT, OUTPUT);
    pinMode(VARIN1_GPIOIN1_BIT_PIN_BIT, INPUT_PULLUP);

    Serial.begin(115200);
    Serial.setTimeout(10);
    Serial1.begin(1000000);
    Serial1.setTimeout(1);
    delay(100);
}

void loop() {


    VARIN1_GPIOIN1_BIT = digitalRead(VARIN1_GPIOIN1_BIT_PIN_BIT);

    rio_rtx();


    digitalWrite(VAROUT1_GPIOOUT9_BIT_PIN_BIT, VAROUT1_GPIOOUT9_BIT);

}
