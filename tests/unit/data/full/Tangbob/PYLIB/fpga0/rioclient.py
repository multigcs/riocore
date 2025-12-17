#!/usr/bin/env python3
#
#

import sys
import time
from rio import RioWrapper

def set_values(rio):
    rio.data_set("SIGOUT_FPGA0_STEPDIR0_VELOCITY", 0.0)
    rio.data_set("SIGOUT_FPGA0_STEPDIR0_ENABLE", 0)
    rio.data_set("SIGOUT_FPGA0_STEPDIR1_VELOCITY", 0.0)
    rio.data_set("SIGOUT_FPGA0_STEPDIR1_ENABLE", 0)
    rio.data_set("SIGOUT_FPGA0_STEPDIR2_VELOCITY", 0.0)
    rio.data_set("SIGOUT_FPGA0_STEPDIR2_ENABLE", 0)
    rio.data_set("SIGOUT_FPGA0_FPGA0_WLED_0_GREEN", 0)
    rio.data_set("SIGOUT_FPGA0_FPGA0_WLED_0_BLUE", 0)
    rio.data_set("SIGOUT_FPGA0_FPGA0_WLED_0_RED", 0)
    rio.data_set("SIGOUT_FPGA0_BITOUT0_BIT", 0)

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
