
#include <unistd.h>
#include <stdint.h>
#include <stdlib.h>
#include <stdbool.h>
#include <stdio.h>
#include <string.h>

#include <rio.h>

data_t *data;

int set_values(void) {
    *data->SIGOUT_BOARD0_BITOUT0_BIT = 0;
    *data->SIGOUT_BOARD0_BITOUT1_BIT = 0;
    *data->SIGOUT_BOARD0_PWMOUT0_DTY = 0.0;
    *data->SIGOUT_BOARD0_PWMOUT0_ENABLE = 0;
    *data->SIGOUT_BOARD0_STEPDIR0_VELOCITY = 0.0;
    *data->SIGOUT_BOARD0_STEPDIR0_ENABLE = 0;
}

int print_values(void) {
    printf("SIGIN_BOARD0_BITIN0_BIT: %i\n", *data->SIGIN_BOARD0_BITIN0_BIT);
    printf("SIGIN_BOARD0_STEPDIR0_POSITION: %f\n", *data->SIGIN_BOARD0_STEPDIR0_POSITION);
    printf("\n");
}

int main(int argc, char **argv) {
    data = init(argc, argv);

    while (1) {
        set_values();
        rio_readwrite(NULL, 0);
        print_values();

        usleep(100000);
    }

    return 0;
}
