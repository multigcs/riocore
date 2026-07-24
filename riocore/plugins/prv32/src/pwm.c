
#include "rio.h"

#ifdef PWM0_DIV

void pwm_set(unsigned int pwm, unsigned int percent) {
    *PWM0_PULSE = PWM0_DIV * percent / 100;
}

#endif
