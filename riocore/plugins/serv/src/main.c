
#include <stdint.h>

#define GPIOS ((volatile unsigned int *) 0x80000000)
#define INPUT  0
#define OUTPUT 1
#define LOW    0
#define HIGH   1
#define TOGGLE 2

// GPIO functions
void pinMode(uint8_t num, uint8_t dir) {
    if (dir == OUTPUT) {
        *GPIOS |= (1<<(num + 16));
    } else {
        *GPIOS &= ~(1<<(num + 16));
    }
}

void digitalWrite(uint8_t num, uint8_t value) {
    if (value == HIGH) {
        *GPIOS |= (1<<num);
    } else if (value == LOW) {
        *GPIOS &= ~(1<<num);
    } else if (TOGGLE) {
        if ((*GPIOS & (1<<num)) != 0) {
            *GPIOS &= ~(1<<num);
        } else {
            *GPIOS |= (1<<num);
        }
    }
}

uint8_t digitalRead(uint8_t num) {
    if ((*GPIOS & (1<<num)) != 0) {
        return HIGH;
    }
    return LOW;
}

static inline void delay(uint32_t delay) {
    for (int i = 0; i < delay; i++) {
        asm("nop");
    }
}

int main() {
    pinMode(0, OUTPUT);
    pinMode(1, OUTPUT);
    digitalWrite(0, HIGH);
    digitalWrite(1, LOW);
    while (1) {
        digitalWrite(0, LOW);
        digitalWrite(1, HIGH);
        delay(0x20000);
        digitalWrite(0, HIGH);
        digitalWrite(1, HIGH);
        delay(0x20000);
        digitalWrite(0, HIGH);
        digitalWrite(1, LOW);
        delay(0x20000);
        digitalWrite(0, HIGH);
        digitalWrite(1, HIGH);
        delay(0x20000);
        digitalWrite(0, LOW);
        digitalWrite(1, LOW);
        delay(0x20000);
        digitalWrite(0, HIGH);
        digitalWrite(1, HIGH);
        delay(0x20000);
    }
    return 0;
}
