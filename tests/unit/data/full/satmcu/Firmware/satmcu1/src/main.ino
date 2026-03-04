
int rxPin = 1;
int txPin = 0;

#define MCU_BUFFER_SIZE_TX 5
#define MCU_BUFFER_SIZE_RX 5

uint8_t tx_buffer[MCU_BUFFER_SIZE_TX + 1] = {0x64, 0x61, 0x74, 0x61,  0, 0};
uint8_t rx_buffer[MCU_BUFFER_SIZE_RX + 1] = {0, 0, 0, 0,  0, 0};

bool VAROUT1_GPIOOUT9_BIT = 0;
bool VARIN1_GPIOIN1_BIT = 0;

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
                VAROUT1_GPIOOUT9_BIT = 1;
            } else {
                VAROUT1_GPIOOUT9_BIT = 0;
            }
            received_ok = 1;
        }
    }
    if (received_ok == 1) {
        // write tx_buffer
        if (VARIN1_GPIOIN1_BIT == 1) {
            tx_buffer[4] |= (1<<7);
        } else {
            tx_buffer[4] &= ~(1<<7);
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


void setup() {
    Serial.begin(115200);
    Serial.setTimeout(10);
    Serial1.begin(1000000);
    Serial1.setTimeout(1);
    delay(100);
}

void loop() {
    rio_rtx();
}
