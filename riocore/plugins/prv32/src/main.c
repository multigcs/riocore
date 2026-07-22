
#include <rio.h>

int main() {
    #ifdef GPIO_LED0
        pinMode(GPIO_LED0, OUTPUT);
        digitalWrite(GPIO_LED0, HIGH);
    #endif

    #ifdef GPIO_LED1
        pinMode(GPIO_LED1, OUTPUT);
        digitalWrite(GPIO_LED1, LOW);
    #endif

    #ifdef GPIO_SW
        pinMode(GPIO_SW, INPUT);
    #endif

    #ifdef UART0_DIV
        uart_set_div(0, UART_B115200);
        uart_puts(0, SYSNAME);
        uart_puts(0, ": hello world\r\n");
    #endif

    uint32_t last = mills();
    while (1) {
        
        uint32_t now = mills();
        if (now - last > 100) {
            last = now;

            #ifdef UART0_DIV

                if (uart_available(0)) {
                    char rx = uart_getchar(0);
                    uart_puts(0, "rec: ");
                    uart_putc(0, rx);
                    uart_puts(0, "\r\n");
                }

                uart_puts(0, SYSNAME);
                uart_puts(0, " - ");
                #ifdef ENABLE_MUL__
                    uart_print_dec(0, now / 100);
                #else
                    uart_print_hex(0, now);
                #endif
                uart_puts(0, ": Loop\r\n");
            #endif

            #ifdef GPIO_LED0
                digitalWrite(GPIO_LED0, TOGGLE);
            #endif
            #ifdef GPIO_LED1
                #ifndef GPIO_SW
                    digitalWrite(GPIO_LED1, TOGGLE);
                #endif
            #endif
        }

        #ifdef RIO_VIN0
            #ifdef RIO_VOUT0
                RIO_VIN0 = RIO_VOUT0 + 20;
            #else
                RIO_VIN0 = 123;
            #endif
        #endif

        #ifdef GPIO_LED1
            #ifdef GPIO_SW
                digitalWrite(GPIO_LED1, digitalRead(GPIO_SW));
            #endif
        #endif
    }
    return 0;
}
