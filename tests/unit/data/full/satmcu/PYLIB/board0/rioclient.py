#!/usr/bin/env python3
#
#

import sys
import time
from rio import RioWrapper

def set_values(rio):
    rio.data_set("SIGOUT_BOARD0_STEPDIR0_VELOCITY", 0.0)
    rio.data_set("SIGOUT_BOARD0_STEPDIR0_ENABLE", 0)
    rio.data_set("SIGOUT_BOARD0_STEPDIR1_VELOCITY", 0.0)
    rio.data_set("SIGOUT_BOARD0_STEPDIR1_ENABLE", 0)
    rio.data_set("SIGOUT_BOARD0_STEPDIR2_VELOCITY", 0.0)
    rio.data_set("SIGOUT_BOARD0_STEPDIR2_ENABLE", 0)
    rio.data_set("SIGOUT_BOARD0_BITOUT0_BIT", 0)
    rio.data_set("SIGOUT_BOARD0_BITOUT1_BIT", 0)
    rio.data_set("SIGOUT_BOARD0_SATMCU0_GPIOOUT0_BIT", 0)
    rio.data_set("SIGOUT_BOARD0_SATMCU0_GPIOOUT1_BIT", 0)
    rio.data_set("SIGOUT_BOARD0_SATMCU0_GPIOOUT2_BIT", 0)
    rio.data_set("SIGOUT_BOARD0_SATMCU0_GPIOOUT3_BIT", 0)
    rio.data_set("SIGOUT_BOARD0_SATMCU0_GPIOOUT4_BIT", 0)
    rio.data_set("SIGOUT_BOARD0_SATMCU0_GPIOOUT5_BIT", 0)
    rio.data_set("SIGOUT_BOARD0_SATMCU0_GPIOOUT6_BIT", 0)
    rio.data_set("SIGOUT_BOARD0_SATMCU0_GPIOOUT7_BIT", 0)
    rio.data_set("SIGOUT_BOARD0_SATMCU0_GPIOOUT8_BIT", 0)
    rio.data_set("SIGOUT_BOARD0_SATMCU1_GPIOOUT9_BIT", 0)

def print_values(rio):
    for name, config in rio.data_info().items():
        if config["direction"] == "input":
            print(f'{config["halname"]} = {rio.data_get(name)}')
    print("")

rio = RioWrapper(sys.argv)

while True:
    set_values(rio)
    rio.rio_readwrite()
    print_values(rio)
    time.sleep(0.1)
