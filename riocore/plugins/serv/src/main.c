
#include <rio.h>

int main() {
    pinMode(GPIO_LED0, OUTPUT);
    pinMode(GPIO_LED1, OUTPUT);
    pinMode(GPIO_LED2, OUTPUT);
    digitalWrite(GPIO_LED0, LOW);
    digitalWrite(GPIO_LED1, LOW);
    digitalWrite(GPIO_LED2, LOW);

    while (1) {

        RIO_SWIN = 1 - digitalRead(GPIO_SW1);

        digitalWrite(GPIO_LED0, LOW);
        if (RIO_SET > RIO_GET) {
            RIO_DONE = 0;
            digitalWrite(GPIO_LED1, LOW);
            RIO_GET = RIO_GET + 1;
        } else if (RIO_SET < RIO_GET) {
            RIO_DONE = 0;
            digitalWrite(GPIO_LED2, LOW);
            RIO_GET = RIO_GET - 1;
        } else {
            RIO_DONE = 1;
        }
        delay(0x1000);
        digitalWrite(GPIO_LED0, HIGH);
        digitalWrite(GPIO_LED1, HIGH);
        digitalWrite(GPIO_LED2, HIGH);
        delay(0x1000);
    }
    return 0;
}
