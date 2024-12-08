#!/usr/bin/env python3
#
#
"""

loadusr -Wn spnav ./spnav.py

setp spnav.axis.x.scale -0.2
setp spnav.axis.y.scale -0.2
setp spnav.axis.z.scale 0.2
setp spnav.axis.a.scale 0.02
setp spnav.axis.b.scale 0.02
setp spnav.axis.c.scale 0.02

net spnav_x <= spnav.axis.x.jog-counts
net spnav_x => axis.x.jog-counts
setp axis.x.jog-vel-mode 1
setp axis.x.jog-enable 1
setp axis.x.jog-scale 0.01

net spnav_y <= spnav.axis.y.jog-counts
net spnav_y => axis.y.jog-counts
setp axis.y.jog-vel-mode 1
setp axis.y.jog-enable 1
setp axis.y.jog-scale 0.01

net spnav_z <= spnav.axis.z.jog-counts
net spnav_z => axis.z.jog-counts
setp axis.z.jog-vel-mode 1
setp axis.z.jog-enable 1
setp axis.z.jog-scale 0.01


net spnav_c <= spnav.axis.c.jog-counts
net spnav_c => axis.c.jog-counts
setp axis.c.jog-vel-mode 1
setp axis.c.jog-enable 1
setp axis.c.jog-scale 0.01


"""
import sys
import spacenav
import atexit

JOINTS = 6
DEADBAND = 50


try:
    import hal

    h = hal.component("spnav")
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

try:
    spacenav.open()
    atexit.register(spacenav.close)
    print("SPNAV: connected")
except spacenav.ConnectionError:
    print("SPNAV: No connection to the SpaceNav driver")
    sys.exit(-1)

stop = False

while not stop:
    event = spacenav.wait()

    if type(event) is spacenav.ButtonEvent:
        h[f"button.{event.button}"] = event.pressed
    else:
        mapping = {
            "x": {"axis": "x",},
            "y": {"axis": "z",},
            "z": {"axis": "y",},
            "rx": {"axis": "a",},
            "ry": {"axis": "c",},
            "rz": {"axis": "b",},
        }
        for in_axis, setup in mapping.items():
            value = getattr(event, in_axis)
            if abs(value) > DEADBAND:
                out_axis = setup["axis"]
                scale = h[f"axis.{out_axis}.scale"]
                h[f"axis.{out_axis}.jog-counts"] += int(value * scale)

