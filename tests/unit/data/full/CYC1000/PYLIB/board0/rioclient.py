#!/usr/bin/python3
#
#

import sys
import time
from rio import RioWrapper

def set_values(rio):
    rio.data_set("SIGOUT_BOARD0_BITOUT0_BIT", 0)
    rio.data_set("SIGOUT_BOARD0_BITOUT1_BIT", 0)
    rio.data_set("SIGOUT_BOARD0_PWMOUT0_DTY", 0.0)
    rio.data_set("SIGOUT_BOARD0_PWMOUT0_ENABLE", 0)
    rio.data_set("SIGOUT_BOARD0_STEPDIR0_VELOCITY", 0.0)
    rio.data_set("SIGOUT_BOARD0_STEPDIR0_ENABLE", 0)

def print_values(rio):
    for name, config in rio.data_info().items():
        if config["direction"] == "input":
            print(f'{config["halname"]} = {rio.data_get(name)}')
    print("")

rio = RioWrapper()

while True:
    set_values(rio)
    rio.rio_readwrite()
    print_values(rio)
    time.sleep(0.1)
