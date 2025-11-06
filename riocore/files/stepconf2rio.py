#!/usr/bin/env python3
#
#

import sys
import json
from lxml import etree

template = {
    "name": "Parport",
    "plugins": [],
    "flow": {
        "view": {
            "scale": 1.0,
            "pos": [-10, -10],
        },
        "board": {
            "pos": [
                0,
                0,
            ],
            "rotate": 0,
        },
    },
}

stepconf = sys.argv[1]
xml_data = open(stepconf, "r").read()
stepconf_keys = {}
stepconf_values = {}
stepconf_types = {}

root = etree.fromstring(xml_data)
for child in root:
    if child.tag == "property":
        vtype = child.get("type")
        name = child.get("name")
        value = child.get("value")
        stepconf_keys[name] = value
        stepconf_values[value] = name
        stepconf_types[name] = vtype


template["plugins"].append(
    {
        "type": "parport",
        "uid": "parport0",
        "pos": [
            0,
            0,
        ],
        "rotate": 0,
        "name": "pport",
    },
)


# stepgen
plugin_py = 0
for joint_n, axis in enumerate("xyzabcuvw"):
    pin_step = stepconf_values.get(f"{axis}step")
    pin_dir = stepconf_values.get(f"{axis}dir")
    if pin_step and pin_dir:
        inv_step = stepconf_keys.get(f"{pin_step}inv")
        inv_dir = stepconf_keys.get(f"{pin_dir}inv")
        stepgen = {
            "type": "stepgen",
            "axis": axis.upper(),
            "is_joint": True,
            "joint": {},
            "pins": {"step": {"pin": f"parport0:DB25:P{pin_step[3:]}"}, "dir": {"pin": f"parport0:DB25:P{pin_dir[3:]}"}},
            "pos": [400, plugin_py],
        }
        mod_py = plugin_py
        plugin_py += 100
        if inv_step == "True":
            stepgen["pins"]["step"]["modifier"] = [
                {
                    "type": "invert",
                    "pos": [200, mod_py],
                },
            ]
            mod_py += 50
        if inv_dir == "True":
            stepgen["pins"]["dir"]["modifier"] = [
                {
                    "type": "invert",
                    "pos": [200, mod_py],
                },
            ]
            mod_py += 50

        mapping = {
            "scale": "scale",
            "min_limit": "minlim",
            "max_limit": "maxlim",
            "max_velocity": "maxvel",
            "max_acceleration": "maxacc",
            "home": "homepos",
            "home_offset": "homesw",
            "home_search_vel": "homevel",
        }
        for rio_name, sc_name in mapping.items():
            value = stepconf_keys.get(f"{axis}{sc_name}")
            vtype = stepconf_types.get(f"{axis}{sc_name}")
            if value is not None:
                if vtype == "float":
                    stepgen["joint"][rio_name] = float(value)
                elif vtype == "bool":
                    stepgen["joint"][rio_name] = bool(value)
                elif vtype == "int":
                    stepgen["joint"][rio_name] = int(value)
        stepgen["joint"]["home_latch_vel"] = 1.5
        if stepconf_keys.get(f"{axis}latchdir") == "1":
            stepgen["joint"]["home_latch_vel"] *= -1
        template["plugins"].append(stepgen)

        pin_home = stepconf_values.get(f"home-{axis}")
        if pin_home:
            inv_home = stepconf_keys.get(f"{pin_home}inv")
            gpioin = {
                "type": "gpioin",
                "pins": {"bit": {"pin": f"parport0:DB25:P{pin_home[3:]}"}},
                "pos": [400, plugin_py],
                "signals": {
                    "bit": {
                        "net": f"joint.{joint_n}.home-sw-in",
                    }
                },
            }
            mod_py = plugin_py
            plugin_py += 100
            if inv_home == "True":
                gpioin["pins"]["bit"]["modifier"] = [
                    {
                        "type": "invert",
                        "pos": [200, mod_py],
                    },
                ]
                mod_py += 50
            template["plugins"].append(gpioin)


# pwmgen
spindle_cw = stepconf_keys.get("spindle-cw")
spindle_pwm = stepconf_keys.get("spindle-pwm")
spindlecarrier = stepconf_keys.get("spindlecarrier")
spindlecpr = stepconf_keys.get("spindlecpr")
spindlefiltergain = stepconf_keys.get("spindlefiltergain")
spindlenearscale = stepconf_keys.get("spindlenearscale")
spindlepwm1 = stepconf_keys.get("spindlepwm1")
spindlepwm2 = stepconf_keys.get("spindlepwm2")
spindlespeed1 = stepconf_keys.get("spindlespeed1")
spindlespeed2 = stepconf_keys.get("spindlespeed2")
# calc
spindlepwm_diff = float(spindlepwm2) - float(spindlepwm1)
spindlespeed_diff = float(spindlespeed2) - float(spindlespeed1)
scale = spindlespeed_diff / spindlepwm_diff
offset = float(spindlepwm1) - float(spindlespeed1) / scale
# pins
pin_pwm = stepconf_values.get("spindle-pwm")
pin_cw = stepconf_values.get("spindle-cw")
pin_pwm_inv = stepconf_keys.get(f"{pin_pwm}inv")
pin_cw_inv = stepconf_keys.get(f"{pin_cw}inv")
pwmgen = {
    "type": "pwmgen",
    "pwm-freq": float(spindlecarrier),
    "scale": scale,
    "offset": offset,
    "min-dc": float(spindlepwm1),
    "max-dc": float(spindlepwm2),
    "dither-pwm": True,
    "signals": {"value": {"net": "spindle.0.speed-out"}, "enable": {"net": "spindle.0.on"}},
    "pins": {"pwm": {"pin": f"parport0:DB25:P{pin_pwm[3:]}"}, "dir": {"pin": f"parport0:DB25:P{pin_cw[3:]}"}},
    "pos": [400, plugin_py],
}
mod_py = plugin_py
plugin_py += 100
if pin_pwm_inv == "True":
    pwmgen["pins"]["pwm"]["modifier"] = [
        {
            "type": "invert",
            "pos": [
                200,
                mod_py,
            ],
        },
    ]
    mod_py += 50
if pin_cw_inv == "True":
    pwmgen["pins"]["cw"]["modifier"] = [
        {
            "type": "invert",
            "pos": [
                200,
                mod_py,
            ],
        },
    ]
    mod_py += 50


template["plugins"].append(pwmgen)

json_data = json.dumps(template, indent=4)
print(json_data)
