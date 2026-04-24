#!/usr/bin/env python3
#
#

import argparse
import json
import os
import sys

if os.path.isfile(os.path.join("riocore", "__init__.py")):
    sys.path.insert(0, os.getcwd())
elif os.path.isfile(os.path.join(os.path.dirname(os.path.dirname(__file__)), "riocore", "__init__.py")):
    sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import sexp

import riocore

riocore_path = os.path.dirname(riocore.__file__)

parser = argparse.ArgumentParser()
parser.add_argument("--list", "-l", help="list all plugins", default=False, action="store_true")
parser.add_argument("--generate", "-g", help="generate readme files for all plugins", default=False, action="store_true")
parser.add_argument("plugin", help="plugin", nargs="?", type=str, default=None)
parser.add_argument("--renew", "-r", help="renew kicad images", default=False, action="store_true")
args = parser.parse_args()

if args.list:
    plugins = riocore.Plugins()
    for plugin in plugins.list():
        plugins.load_plugins({"plugins": [{"type": plugin["name"]}]})

    print("Interfaces:")
    print()
    for plugin_instance in plugins.plugin_instances:
        if plugin_instance.TYPE == "interface":
            print(f"  {plugin_instance.NAME:20s} {plugin_instance.INFO}")
    print()

    print("Expansions:")
    print()
    for plugin_instance in plugins.plugin_instances:
        if plugin_instance.TYPE == "expansion":
            print(f"  {plugin_instance.NAME:20s} {plugin_instance.INFO}")
    print()

    print("Joints:")
    print()
    for plugin_instance in plugins.plugin_instances:
        if plugin_instance.TYPE == "joint":
            print(f"  {plugin_instance.NAME:20s} {plugin_instance.INFO}")
    print()

    print("IO:")
    print()
    for plugin_instance in plugins.plugin_instances:
        if plugin_instance.TYPE == "io":
            print(f"  {plugin_instance.NAME:20s} {plugin_instance.INFO}")
    print()

elif args.generate:
    plugins = riocore.Plugins()
    for plugin in plugins.list():
        filename = os.path.join("riocore", "plugins", plugin["name"], "README.md")
        print(filename)
        text = plugins.info(plugin["name"])
        open(filename, "w").write(text)

    filename = "riocore/plugins/README.md"
    print(filename)
    text = []

    text.append("# PLUGINS")
    text.append("")
    text.append("| Type | Name | Info | Image | Comment |")
    text.append("| --- | :---: | --- | :---: | :---: |")

    for title_raw, ptype in {
        "Interfaces": "interface",
        "Joints": "joint",
        "IO": "io",
        "FrameIO": "frameio",
        "Expansions": "expansion",
        "Misc": "base",
    }.items():
        # text.append(f"## {title}:")
        # text.append("")
        title = title_raw
        for plugin_instance in plugins.plugin_instances:
            if ptype == plugin_instance.TYPE:
                image = ""
                plugin_path = os.path.join(riocore_path, "plugins", plugin_instance.NAME)
                image_path = os.path.join(plugin_path, "image.png")
                if os.path.isfile(image_path):
                    image = f'<img src="{plugin_instance.NAME}/image.png" height="48">'
                comments = ""
                if plugin_instance.EXPERIMENTAL:
                    comments += "Experimental "

                text.append(f"| {title} | [{plugin_instance.NAME}]({plugin_instance.NAME}/README.md) | {plugin_instance.INFO} | {image} | {comments} |")
                title = ""

                if "node_type" in plugin_instance.OPTIONS:
                    for node_type in plugin_instance.OPTIONS["node_type"]["options"]:
                        for kicad_module in plugin_instance.KICAD_MODULES:
                            pcb_path = os.path.join(plugin_path, plugin_instance.KICAD_FOLDER, node_type, kicad_module, f"{kicad_module}.kicad_pcb")
                            if os.path.isfile(pcb_path):
                                pass

                else:
                    for kicad_module in plugin_instance.KICAD_MODULES:
                        pcb_path = os.path.join(plugin_path, plugin_instance.KICAD_FOLDER, kicad_module, f"{kicad_module}.kicad_pcb")
                        if not os.path.isfile(pcb_path):
                            continue
                        pcb_data = sexp.loads(open(pcb_path, "r").read())
                        dim = sexp.pcb_dimentions(pcb_data)
                        info = {"dimentions": dim, "pins": {}}
                        for pin in plugin_instance.PINDEFAULTS:
                            if ":" in pin:
                                continue
                            for entry in pcb_data:
                                if entry[0] != "footprint":
                                    continue
                                fat = ("0", "0")
                                for sentry in entry[2:]:
                                    if sentry[0] == "at":
                                        fat = sentry[1:]
                                for sentry in entry[2:]:
                                    if sentry[0] != "pad":
                                        continue
                                    at = None
                                    net = None
                                    size = ["0", "0"]
                                    for ssentry in sentry[3:]:
                                        if ssentry[0] == "at":
                                            at = ssentry[1:3]
                                        elif ssentry[0] == "net":
                                            net = ssentry[2].strip('"')
                                        elif ssentry[0] == "size":
                                            size = ssentry[1:3]
                                    if net == f"/{pin}" and at:
                                        fat_x = float(fat[0])
                                        fat_y = float(fat[1])
                                        at_x = float(at[0]) + float(size[0]) / 2
                                        at_y = float(at[1]) + float(size[1]) / 2
                                        fat_r = 0.0
                                        if len(fat) == 3:
                                            fat_r = float(fat[2].strip('"'))
                                        nrot = 0
                                        if fat_r:
                                            at_x, at_y = sexp.rotate_point((0, 0), (at_x, at_y), fat_r)
                                        info["pins"][pin] = {
                                            "pos": [
                                                ((float(fat_x) + at_x) - dim["start_x"]) * 4.2,
                                                ((float(fat_y) + at_y) - dim["start_y"]) * 4.2,
                                            ]
                                        }

                        info_path = os.path.join(plugin_path, plugin_instance.KICAD_FOLDER, kicad_module, "info.json")
                        open(info_path, "w").write(json.dumps(info, indent=2))

                        svg_path = os.path.join(plugin_path, plugin_instance.KICAD_FOLDER, kicad_module, f"{kicad_module}-export.svg")
                        png_path = os.path.join(plugin_path, plugin_instance.KICAD_FOLDER, kicad_module, f"{kicad_module}-export.png")

                        renew = args.renew
                        if os.path.exists(png_path):
                            pcb_time = os.path.getmtime(pcb_path)
                            png_time = os.path.getmtime(png_path)
                            if pcb_time > png_time:
                                renew = True

                        if not os.path.exists(png_path) or renew:
                            print("export kicad image")
                            os.system(f"kicad-cli pcb export svg --fit-page-to-board --layers F.Cu,F.SilkS,Edge.Cuts --output '{svg_path}' '{pcb_path}'")
                            os.system(f"inkscape '{svg_path}' --export-type=png --export-filename='{png_path}' --export-dpi=110")
                            os.system(f"rm -rf '{svg_path}'")

    text.append("")

    open(filename, "w").write("\n".join(text))


elif args.plugin:
    plugins = riocore.Plugins()
    print(plugins.info(args.plugin))
