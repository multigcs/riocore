
#include "rio.h"

#ifdef PWM0_TOTAL

void pwm_set_total(unsigned int pwm, unsigned int total) {
    *PWM0_TOTAL = total;
}

void pwm_set_pulse(unsigned int pwm, unsigned int pulse) {
    *PWM0_PULSE = pulse;
}

#endif
