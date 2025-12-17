
#include <unistd.h>
#include <stdint.h>
#include <stdlib.h>
#include <stdbool.h>
#include <stdio.h>
#include <string.h>

#include <rio.h>

data_t *data;

int set_values(void) {
    *data->SIGOUT_FPGA0_STEPDIR0_VELOCITY = 0.0;
    *data->SIGOUT_FPGA0_STEPDIR0_ENABLE = 0;
    *data->SIGOUT_FPGA0_STEPDIR1_VELOCITY = 0.0;
    *data->SIGOUT_FPGA0_STEPDIR1_ENABLE = 0;
    *data->SIGOUT_FPGA0_STEPDIR2_VELOCITY = 0.0;
    *data->SIGOUT_FPGA0_STEPDIR2_ENABLE = 0;
    *data->SIGOUT_FPGA0_FPGA0_WLED_0_GREEN = 0;
    *data->SIGOUT_FPGA0_FPGA0_WLED_0_BLUE = 0;
    *data->SIGOUT_FPGA0_FPGA0_WLED_0_RED = 0;
    *data->SIGOUT_FPGA0_BITOUT0_BIT = 0;
}

int print_values(void) {
    printf("SIGIN_FPGA0_MODBUS0_TEMPERATURE: %f\n", *data->SIGIN_FPGA0_MODBUS0_TEMPERATURE);
    printf("SIGIN_FPGA0_I2CBUS0_LM75_0_TEMP: %f\n", *data->SIGIN_FPGA0_I2CBUS0_LM75_0_TEMP);
    printf("SIGIN_FPGA0_I2CBUS0_LM75_0_VALID: %i\n", *data->SIGIN_FPGA0_I2CBUS0_LM75_0_VALID);
    printf("SIGIN_FPGA0_STEPDIR0_POSITION: %f\n", *data->SIGIN_FPGA0_STEPDIR0_POSITION);
    printf("SIGIN_FPGA0_STEPDIR1_POSITION: %f\n", *data->SIGIN_FPGA0_STEPDIR1_POSITION);
    printf("SIGIN_FPGA0_STEPDIR2_POSITION: %f\n", *data->SIGIN_FPGA0_STEPDIR2_POSITION);
    printf("SIGIN_FPGA0_BITIN0_BIT: %i\n", *data->SIGIN_FPGA0_BITIN0_BIT);
    printf("SIGIN_FPGA0_BITIN1_BIT: %i\n", *data->SIGIN_FPGA0_BITIN1_BIT);
    printf("SIGIN_FPGA0_BITIN2_BIT: %i\n", *data->SIGIN_FPGA0_BITIN2_BIT);
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
