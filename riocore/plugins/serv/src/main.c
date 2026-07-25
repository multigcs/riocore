
#include <rio.h>

int main() {
    pinMode(GPIO_LED0, OUTPUT);
    digitalWrite(GPIO_LED0, LOW);

    while (1) {

        digitalWrite(GPIO_LED0, LOW);
        delay(0x1000);
        digitalWrite(GPIO_LED0, HIGH);
        delay(0x1000);
    }
    return 0;
}
