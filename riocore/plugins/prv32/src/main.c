
#include <rio.h>

int main() {
    int i;
    unsigned char v, ch;

#ifdef UART0_DIV
#ifdef uart_set_baud
    uart_set_baud(0, 9600);
#else
    uart_set_div(0, SYSCLOCK / 9600);
#endif
    uart_puts(0, SYSNAME);
    uart_puts(0, ": hello world\r\n");
#endif

#ifdef GPIO_LED0
    pinMode(GPIO_LED0, OUTPUT);
    digitalWrite(GPIO_LED0, HIGH);
#endif
#ifdef GPIO_LED1
    pinMode(GPIO_LED1, OUTPUT);
    digitalWrite(GPIO_LED1, HIGH);
#endif
#ifdef GPIO_SW
    pinMode(GPIO_SW, INPUT);
#endif

    i = 0;
    while (1) {

#ifdef UART0_DIV
        uart_puts(0, "Loop\r\n");
#endif

#ifdef RIO_VIN0
#ifdef RIO_VOUT0
        *RIO_VIN0 = *RIO_VOUT0 + 20;
#else
        *RIO_VIN0 = 123;
#endif
#endif

#ifdef GPIO_LED0
        digitalWrite(GPIO_LED0, TOGGLE);
#endif
#ifdef GPIO_LED1
#ifdef GPIO_SW
        digitalWrite(GPIO_LED1, digitalRead(GPIO_SW));
#endif
#endif

        delay(100);
        i += 1;
    }

    return 0;
}
