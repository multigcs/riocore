#!/usr/bin/env python3
#
# loadusr -Wn parport ./sim_parport.py cfg="0 out"
# remove all addf parport. entrys from hal
#

import sys
import time

import hal

modes = {
    "in": {
        "inputs": [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 15],
        "outputs": [1, 14, 16, 17],
    },
    "x": {
        "inputs": [1, 10, 11, 12, 13, 14, 15, 16, 17],
        "outputs": [2, 3, 4, 5, 6, 7, 8, 9],
    },
    "out": {
        "inputs": [10, 11, 12, 13, 15],
        "outputs": [1, 2, 3, 4, 5, 6, 7, 8, 9, 14, 16, 17],
    },
    "epp": {
        "inputs": [10, 11, 12, 13, 15],
        "outputs": [1, 2, 3, 4, 5, 6, 7, 8, 9, 14, 16, 17],
    },
}


h = hal.component("parport")

config = {}
last_pnum = None

for part in " ".join(sys.argv[1:]).replace("cfg=", "").replace('"', "").split():
    if part.isnumeric():
        last_pnum = part
        config[last_pnum] = "epp"
    elif last_pnum is not None:
        config[last_pnum] = part

for pnum, mode in config.items():
    for pin in modes[mode]["inputs"]:
        h.newpin(f"{pnum}.pin-{pin:02d}-in", hal.HAL_BIT, hal.HAL_OUT)
        h.newpin(f"{pnum}.pin-{pin:02d}-in-not", hal.HAL_BIT, hal.HAL_OUT)
    for pin in modes[mode]["outputs"]:
        h.newpin(f"{pnum}.pin-{pin:02d}-out", hal.HAL_BIT, hal.HAL_IN)
        h.newpin(f"{pnum}.pin-{pin:02d}-out-reset", hal.HAL_BIT, hal.HAL_IN)
        h.newpin(f"{pnum}.pin-{pin:02d}-out-invert", hal.HAL_BIT, hal.HAL_IN)
    h.newpin(f"{pnum}.reset-time", hal.HAL_U32, hal.HAL_IN)

h.ready()


while True:
    time.sleep(0.5)
