
#include "rio.h"

#ifdef GPIO_SPI0_SCLK

unsigned char spi0_transfer_byte(unsigned char send_val) {
    unsigned char recv_val = 0;

#ifdef GPIO_SPI0_SEL
    digitalWrite(GPIO_SPI0_SEL, LOW);
#endif    
    for (int i = 0; i < 8; i++) {
#ifdef GPIO_SPI0_MOSI
        if (send_val & 0x80) {
            digitalWrite(GPIO_SPI0_MOSI, HIGH);
        } else {
            digitalWrite(GPIO_SPI0_MOSI, LOW);
        }
#endif
        send_val <<= 1;
        digitalWrite(GPIO_SPI0_SCLK, HIGH);
        recv_val <<= 1;

#ifdef GPIO_SPI0_MISO
        if (digitalRead(GPIO_SPI0_MISO)) {
            recv_val |= 0x01;
        }
#endif

        digitalWrite(GPIO_SPI0_SCLK, LOW);
    }

#ifdef GPIO_SPI0_SEL
    digitalWrite(GPIO_SPI0_SEL, HIGH);
#endif

    return recv_val;
}

#endif
