#!/usr/bin/env python3
#
#

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
