#!/usr/bin/env python3
#
#

import argparse
import os

import riocore

riocore_path = os.path.dirname(riocore.__file__)

parser = argparse.ArgumentParser()
parser.add_argument("--list", "-l", help="list all plugins", default=False, action="store_true")
parser.add_argument("--generate", "-g", help="generate readme files for all plugins", default=False, action="store_true")
parser.add_argument("plugin", help="plugin", nargs="?", type=str, default=None)
args = parser.parse_args()

if args.list:
    plugins = riocore.Plugins()
    for plugin in plugins.list():
        plugins.load_plugins({"plugins": [{"type": plugin["name"]}]})

    print("Interfaces:")
    print("")
    for plugin_instance in plugins.plugin_instances:
        if plugin_instance.TYPE == "interface":
            print(f"  {plugin_instance.NAME:20s} {plugin_instance.INFO}")
    print("")

    print("Expansions:")
    print("")
    for plugin_instance in plugins.plugin_instances:
        if plugin_instance.TYPE == "expansion":
            print(f"  {plugin_instance.NAME:20s} {plugin_instance.INFO}")
    print("")

    print("Joints:")
    print("")
    for plugin_instance in plugins.plugin_instances:
        if plugin_instance.TYPE == "joint":
            print(f"  {plugin_instance.NAME:20s} {plugin_instance.INFO}")
    print("")

    print("IO:")
    print("")
    for plugin_instance in plugins.plugin_instances:
        if plugin_instance.TYPE == "io":
            print(f"  {plugin_instance.NAME:20s} {plugin_instance.INFO}")
    print("")

elif args.generate:
    plugins = riocore.Plugins()
    for plugin in plugins.list():
        filename = f"riocore/plugins/{plugin['name']}/README.md"
        print(filename)
        text = plugins.info(plugin["name"])
        open(filename, "w").write(text)

    filename = "PLUGINS.md"
    print(filename)
    text = []

    text.append("# PLUGINS")
    text.append("")
    text.append("| Type | Name | Info | Image |")
    text.append("| --- | :---: | --- | :---: |")

    for title, ptype in {
        "Interfaces": "interface",
        "Joints": "joint",
        "IO": "io",
        "FrameIO": "frameio",
        "Expansions": "expansion",
    }.items():
        # text.append(f"## {title}:")
        # text.append("")

        for plugin_instance in plugins.plugin_instances:
            if plugin_instance.TYPE == ptype:
                image = ""
                plugin_path = f"{riocore_path}/plugins/{plugin_instance.NAME}"
                image_path = f"{plugin_path}/image.png"
                if os.path.isfile(image_path):
                    image = f'<img src="riocore/plugins/{plugin_instance.NAME}/image.png" height="48">'

                text.append(f"| {title} | [{plugin_instance.NAME}](riocore/plugins/{plugin_instance.NAME}/README.md) | {plugin_instance.INFO} | {image} |")

                title = ""

    text.append("")

    open(filename, "w").write("\n".join(text))


elif args.plugin:
    plugins = riocore.Plugins()
    print(plugins.info(args.plugin))
