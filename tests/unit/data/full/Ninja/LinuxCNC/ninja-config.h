
#ifndef CONFIG_H
#define CONFIG_H
#include "internals.h"

    #define DEFAULT_MAC {00, 0x08, 0xDC, 0x12, 0x34, 0x56}
    #define DEFAULT_IP {192, 168, 0, 177}
    #define DEFAULT_PORT 8888
    #define DEFAULT_GATEWAY {192, 168, 10, 1}
    #define DEFAULT_SUBNET {255, 255, 255, 0}
    #define DEFAULT_TIMEOUT 1000000

    #define breakout_board 0
    #define io_expanders 0

    #define stepgens 3
    #define stepgen_steps {GP00, GP02, GP04}
    #define stepgen_dirs {GP01, GP03, GP05}
    #define step_invert {0, 0, 0}
    #define default_pulse_width 2000
    #define default_step_scale 1000

    #define encoders 0
    #define enc_pins {}
    // #define enc_pins_b {}
    #define enc_index_pins {}
    #define enc_index_active_level {}

    #define in_pins {GP08, GP09, GP10}
    #define in_pullup {1, 1, 1}

    #define out_pins {GP26, GP25, GP29}

    #define use_pwm 1
    #define pwm_count 1
    #define pwm_pin {GP13}
    #define pwm_invert {0}
    #define default_pwm_frequency 10000
    #define default_pwm_maxscale 4096
    #define default_pwm_min_limit 0

    #define raspberry_pi_spi 0
    #define raspi_int_out 25
    #define raspi_inputs {2, 3, 4, 14, 15, 16, 17, 18, 20, 21, 22, 23, 24, 27}
    #define raspi_input_pullups {0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0}
    #define raspi_outputs {0, 1, 5, 6, 12, 13, 19, 26}
    //#define KBMATRIX

#include "footer.h"
#include "kbmatrix.h"
#endif
