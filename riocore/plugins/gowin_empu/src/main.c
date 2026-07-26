
#include "rio.h"

int main() {
    unsigned char val = 1;
    uart_init(UART0, F_CPU / 115200);

    gpio_init();
    gpio_set_dir(0, GPIO_OUT);
    gpio_out_set_val(0, val);

    RIO_GET = 0x123;

    while (1) {

        val = 1 - val;
        gpio_out_set_val(0, val);

        for (int i = 0; i < 100000; i++) {
            asm("nop");
        }

        uart_puts(UART0, "loop ");
        uart_print_hex(UART0, RIO_SET);
        uart_puts(UART0, " ");
        uart_print_hex(UART0, RIO_GET);

        uart_puts(UART0, "\r\n");

    }

    return 0;
}
