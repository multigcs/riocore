#!/usr/bin/python3
#
#

import argparse
import json
import os
import riocore

parser = argparse.ArgumentParser()
parser.add_argument("csv", help="csv input file", nargs="?", type=str, default=None)
args = parser.parse_args()

if not args.csv:
    print("no csv file found.")
    print("")
    print("csv example (PIN;PLUGIN;NUM;PINNAME):")
    print("""
14;spi;1;mosi
17;spi;1;miso
15;spi;1;sclk
32;spi;1;sel
13;stepdir;1;step
12;stepdir;1;dir
11;stepdir;2;step
10;stepdir;2;dir
44;bitout
43;bitout
41;bitin
40;bitin
45;enable
    """)
    print("")
    print("each line needs an FPGA-PIN and plugin-name")
    print("if the plugin have multiple pins,")
    print(" then you need also a instance-number and the pinname")
    print("")
    exit(1)

csv_data = open(args.csv, "r").read()


riocore_path = os.path.dirname(riocore.__file__)
pluginpins = {}
plugins = riocore.Plugins()
for plugin_info in plugins.list():
    plugins.load_plugins({"plugins": [{"type": plugin_info["name"]}]})
    plugin = plugins.plugin_instances[-1]
    pluginpins[plugin_info["name"]] = plugin.PINDEFAULTS

pnums = {}
plugins = {}
for line in csv_data.split("\n"):
    if not line.strip():
        continue
    parts = line.split(";")
    pin = parts[0]
    modifier = []

    if not pin[0]:
        continue

    if pin[0] == "!":
        pin = pin[1:]
        modifier = [{"type": "invert"}]

    if len(parts) == 4 and parts[3]:
        plugin = parts[1]
        pnum = parts[2]
        pinname = parts[3]
    elif len(parts) == 3 and parts[2]:
        plugin = parts[1]
        pnum = ""
        pinname = parts[2]
    elif len(parts) == 2 and parts[1]:
        plugin = parts[1]
        pnum = ""
        pinname = ""
    else:
        continue

    if plugin in pluginpins:
        if pinname:
            if pinname not in pluginpins[plugin]:
                print(f"pin {pinname} not found in {plugin}: {list(pluginpins[plugin].keys())}")
                continue
        else:
            pinname = list(pluginpins[plugin].keys())[0]
    elif plugin == "enable":
        plugin = "bitout"
        pnum = ""
        pinname = "pin"
        modifier = [{"type": "invert"}, {"type": "onerror"}]

    else:
        print(f"plugin not found: {plugin}")
        continue

    if not pnum:
        if plugin not in pnums:
            pnums[plugin] = 0
        pnums[plugin] += 1
        pnum = str(pnums[plugin])

    # print(plugin, pnum, pinname, pluginpins[plugin][pinname])

    pid = f"{plugin}_{pnum}"
    if pid not in plugins:
        plugins[pid] = {"type": plugin, "name": pid, "pins": {}}
    plugins[pid]["pins"][pinname] = {"pin": str(pin)}
    if modifier:
        plugins[pid]["pins"][pinname]["modifier"] = modifier

print(json.dumps({"plugins": list(plugins.values())}, indent=4))
