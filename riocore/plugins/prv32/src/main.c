
#include <rio.h>

int main() {
    int i;
    unsigned char v, ch;

    uart_set_div(0, SYSCLOCK / 9600);
    uart_puts(0, "hello world\r\n");

    pinMode(0, OUTPUT);
    pinMode(1, OUTPUT);
    pinMode(2, OUTPUT);
    pinMode(3, OUTPUT);
    pinMode(4, OUTPUT);
    pinMode(5, OUTPUT);

    digitalWrite(0, HIGH);
    digitalWrite(1, HIGH);
    digitalWrite(2, HIGH);
    digitalWrite(3, HIGH);
    digitalWrite(4, HIGH);
    digitalWrite(5, HIGH);

    pinMode(6, INPUT);
    pinMode(7, INPUT);

    i = 0;
    while (1) {
    uart_puts(0, "Loop\r\n");

        *RIO_VIN = *RIO_VOUT + 20;

        digitalWrite(0, TOGGLE);
        digitalWrite(4, digitalRead(6));
        digitalWrite(5, digitalRead(7));

        cdt_delay(2700000);
        i += 1;
    }

    return 0;
}
