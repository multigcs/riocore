#!/usr/bin/env python3
#
#
"""loadusr -Wn spacenav ./spnav.py

setp spacenav.axis.x.scale -0.2
setp spacenav.axis.y.scale -0.2
setp spacenav.axis.z.scale 0.2
setp spacenav.axis.a.scale 0.02
setp spacenav.axis.b.scale 0.02
setp spacenav.axis.c.scale 0.02

net spacenav_x <= spacenav.axis.x.jog-counts
net spacenav_x => axis.x.jog-counts
setp axis.x.jog-vel-mode 1
setp axis.x.jog-enable 1
setp axis.x.jog-scale 0.01

net spacenav_y <= spacenav.axis.y.jog-counts
net spacenav_y => axis.y.jog-counts
setp axis.y.jog-vel-mode 1
setp axis.y.jog-enable 1
setp axis.y.jog-scale 0.01

net spacenav_z <= spacenav.axis.z.jog-counts
net spacenav_z => axis.z.jog-counts
setp axis.z.jog-vel-mode 1
setp axis.z.jog-enable 1
setp axis.z.jog-scale 0.01

net spacenav_c <= spacenav.axis.c.jog-counts
net spacenav_c => axis.c.jog-counts
setp axis.c.jog-vel-mode 1
setp axis.c.jog-enable 1
setp axis.c.jog-scale 0.01

"""

import atexit
import sys
import time

import spacenav

JOINTS = 6
DEADBAND = 50
MAPPING = {
    "x": {
        "axis": "x",
    },
    "y": {
        "axis": "z",
    },
    "z": {
        "axis": "y",
    },
    "rx": {
        "axis": "a",
    },
    "ry": {
        "axis": "c",
    },
    "rz": {
        "axis": "b",
    },
}

try:
    import hal

    h = hal.component("spacenav")
    for axis in "xyzabc":
        h.newpin(f"axis.{axis}.jog-counts", hal.HAL_S32, hal.HAL_OUT)
        h.newpin(f"axis.{axis}.scale", hal.HAL_FLOAT, hal.HAL_IN)
        h[f"axis.{axis}.jog-counts"] = 0
    h.newpin("button.0", hal.HAL_BIT, hal.HAL_OUT)
    h.newpin("button.1", hal.HAL_BIT, hal.HAL_OUT)
    h.ready()
    no_hal = False
except Exception as error:
    print("starting in test mode", error)
    no_hal = True
    h = {}
    for axis in "xyzabc":
        h[f"axis.{axis}.jog-counts"] = 0
        h[f"axis.{axis}.scale"] = 1.0
    h["button.0"] = 0
    h["button.1"] = 0


def main():
    try:
        spacenav.open()
        atexit.register(spacenav.close)
        print("spacenav: connected")
    except spacenav.ConnectionError:
        print("spacenav: No connection to the SpaceNav driver")
        sys.exit(-1)

    stop = False

    while not stop:
        event = spacenav.poll()
        # event = spacenav.wait()
        if event:
            if type(event) is spacenav.ButtonEvent:
                h[f"button.{event.button}"] = event.pressed
            else:
                for in_axis, setup in MAPPING.items():
                    value = getattr(event, in_axis)
                    if abs(value) > DEADBAND:
                        out_axis = setup["axis"]
                        scale = h[f"axis.{out_axis}.scale"]
                        h[f"axis.{out_axis}.jog-counts"] += int(value * scale)
        if not event:
            time.sleep(0.01)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("exiting spacenav.py")
        sys.exit(130)
