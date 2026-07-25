
#include <rio.h>

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

void delay_nop(uint32_t delay) {
    for (int i = 0; i < delay; i++) {
        asm("nop");
    }
}

// UTIMER
uint32_t mills(void) {
    return *UTIMER;
}
