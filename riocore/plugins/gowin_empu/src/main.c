
#include "rio.h"

int main() {
    sysinit();

    pinMode(GPIO_LED0, OUTPUT);
    digitalWrite(GPIO_LED0, HIGH);

    uint32_t last = mills();
    while (1) {
        uint32_t now = mills();
        if (now - last > 100) {
            last = now;
            digitalWrite(GPIO_LED0, TOGGLE);
        }

        RIO_GET = RIO_SET / 2;
/*
        uart_puts(UART0, "loop ");
        uart_print_hex(UART0, RIO_SET);
        uart_puts(UART0, " ");
        uart_print_hex(UART0, RIO_GET);
        uart_puts(UART0, "\r\n");
*/
    }

    return 0;
}
