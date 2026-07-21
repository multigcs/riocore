
#include <rio.h>

#define BASE ((volatile unsigned int *) 0x0)

int main() {
    uart_set_div(0, UART_B115200);
    uart_puts(0, SYSNAME);
    uart_puts(0, ": hello world\r\n");

    pinMode(GPIO_LED0, OUTPUT);
    digitalWrite(GPIO_LED0, HIGH);
    pinMode(GPIO_LED1, OUTPUT);
    digitalWrite(GPIO_LED1, LOW);

    uint8_t menu = 0;
    uint32_t last = mills();
    while (1) {

        uint32_t now = mills();
        if (now - last > 100) {
            last = now;
            if (menu == 0) {
                uart_puts(0, "counter: ");
                uart_print_dec(0, now);
                uart_puts(0, "\r\n");
            }
           digitalWrite(GPIO_LED0, TOGGLE);
        }

        if (uart_available(0)) {
            char rx = uart_getchar(0);
            if (rx == 'c') {
                menu = 0;

            } else if (rx == 'd') {
                // dump memory
                menu = 1;
                uart_puts(0, "--------------------------------\r\n");
                for (uint32_t i = 0; i < MEMBYTES; i+=4) {
                    uart_print_hex(0, *(uint32_t*)i);
                    uart_puts(0, "\r\n");
                }
                uart_puts(0, "--------------------------------\r\n");

            } else if (rx == 'i') {
                menu = 1;
                uart_puts(0, "\r\n--------------------------------\r\n");
                uart_puts(0, "sysname:   ");
                uart_puts(0, SYSNAME);
                uart_puts(0, "\r\n");
                uart_puts(0, "softcore:  ");
                uart_puts(0, CPU_TYPE);
                uart_puts(0, "\r\n");
                uart_puts(0, "march:     ");
                uart_puts(0, CPU_MARCH);
                uart_puts(0, "\r\n");
                uart_puts(0, "toolchain: ");
                uart_puts(0, FPGA_TOOLCHAIN);
                uart_puts(0, "\r\n");
                uart_puts(0, "family:    ");
                uart_puts(0, FPGA_FAMILY);
                uart_puts(0, "\r\n");
                uart_puts(0, "type:      ");
                uart_puts(0, FPGA_TYPE);
                uart_puts(0, "\r\n");
                uart_puts(0, "f_cpu:     ");
                uart_print_dec(0, F_CPU);
                uart_puts(0, "\r\n");
                uart_puts(0, "--------------------------------\r\n\r\n");
            }
        }
    }
    return 0;
}
