
#include <rio.h>

int main() {
    int i;
    unsigned char v, ch;

#ifdef UART0_DIV
    uart_set_div(0, SYSCLOCK / 9600);
    uart_puts(0, "hello world\r\n");
#endif

    pinMode(0, OUTPUT);
    pinMode(1, OUTPUT);
    pinMode(2, INPUT);

    digitalWrite(0, HIGH);
    digitalWrite(1, HIGH);

    i = 0;
    while (1) {

#ifdef UART0_DIV
        uart_puts(0, "Loop\r\n");
#endif

        *RIO_VIN = *RIO_VOUT + 20;

        digitalWrite(0, TOGGLE);
        digitalWrite(1, digitalRead(2));

        cdt_delay(SYSCLOCK);
        i += 1;
    }

    return 0;
}
