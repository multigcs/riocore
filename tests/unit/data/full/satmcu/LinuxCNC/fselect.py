#!/usr/bin/env python3
#
#

import sys
import time

import hal

halname = "fselect"
values = 3
if len(sys.argv) == 3:
    halname = sys.argv[1]
    values = int(sys.argv[2])

h = hal.component(halname)
for vn in range(values):
    h.newpin(f"value{vn}", hal.HAL_FLOAT, hal.HAL_IN)
    h.newpin(f"in{vn}", hal.HAL_BIT, hal.HAL_IN)
    h.newpin(f"selected{vn}", hal.HAL_BIT, hal.HAL_OUT)
h.newpin("selected", hal.HAL_U32, hal.HAL_OUT)
h.newpin("out", hal.HAL_FLOAT, hal.HAL_OUT)
h["selected"] = 0
h.ready()


try:
    while 1:
        for vn in range(values):
            if h[f"in{vn}"]:
                h["selected"] = vn
                break

        for vn in range(values):
            if h["selected"] == vn:
                h["out"] = h[f"value{vn}"]
                for vn2 in range(values):
                    if vn == vn2:
                        h[f"selected{vn2}"] = 1
                    else:
                        h[f"selected{vn2}"] = 0
                break

        time.sleep(0.1)

except KeyboardInterrupt:
    raise SystemExit
