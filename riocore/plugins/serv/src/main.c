
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
    }

    return 0;
}
