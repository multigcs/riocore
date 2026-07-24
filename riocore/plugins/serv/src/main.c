
#include <stdint.h>

#define GPIO_BASE ((volatile unsigned int *) 0x100)
#define INPUT  0
#define OUTPUT 1
#define LOW    0
#define HIGH   1
#define TOGGLE 2

// GPIO functions
void digitalWrite(uint8_t num, uint8_t value) {
    if (value == HIGH) {
        *GPIO_BASE |= (1<<num);
    } else if (value == LOW) {
        *GPIO_BASE &= ~(1<<num);
    } else if (TOGGLE) {
        if ((*GPIO_BASE & (1<<num)) != 0) {
            *GPIO_BASE &= ~(1<<num);
        } else {
            *GPIO_BASE |= (1<<num);
        }
    }
}

static inline void delay(uint32_t delay) {
    for (int i = 0; i < delay; i++) {
        asm("nop");
    }
}

int main() {
    digitalWrite(1, HIGH);
    while (1) {
        digitalWrite(0, TOGGLE);
        delay(0x20000);
    }
    return 0;
}
