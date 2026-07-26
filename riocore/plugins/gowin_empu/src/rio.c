
#include <rio.h>

void sysinit() {
    gpio_init();
    uart_init(UART0, F_CPU / 115200);
}

// GPIO functions
void pinMode(uint8_t num, uint8_t dir) {
    gpio_set_dir(num, dir);
}

void digitalWrite(uint8_t num, uint8_t value) {
    if (value == HIGH) {
        gpio_out_set_val(num, value);
    } else if (value == LOW) {
        gpio_out_set_val(num, value);
    } else if (TOGGLE) {
        if (gpio_in_get_val(num)) {
            gpio_out_set_val(num, 0);
        } else {
            gpio_out_set_val(num, 1);
        }
    }
}

uint8_t digitalRead(uint8_t num) {
    if (gpio_in_get_val(num)) {
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
