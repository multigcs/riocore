#!/usr/bin/env python3
#
#

import glob
import importlib
import inspect
import json
import os

from riocore.modifiers import Modifiers

examples = {}
for cpath in sorted(glob.glob(os.path.join("riocore", "configs", "*", "config.json"))):
    cjdata = open(cpath).read()
    cdata = json.loads(cjdata)


print("# FPGA-Boards")
output = []
output.append("# BOARDS")
output.append("| Name | Family | Type | Clock | Toolchain | Description | Image |")
output.append("| --- | --- | --- | --- | --- | --- | --- |")
for bpath in sorted(glob.glob(os.path.join("riocore", "plugins", "fpga", "boards", "*.json"))):
    bdata = json.loads(open(bpath).read())
    name = bdata.get("name", "?")
    family = bdata.get("family", "")
    ftype = bdata.get("type", "")
    speed = int(bdata.get("clock", {}).get("speed", "0")) / 1000000
    toolchain = bdata.get("toolchain", "?")
    toolchains = bdata.get("toolchains", [])
    for tc in toolchains:
        if tc != toolchain:
            toolchain += f" ({tc})"
    description = bdata.get("description", "").replace("\n", "<BR/>")
    bimg = ""
    img = ""
    imgfile = bpath.replace(".json", ".png")
    if os.path.isfile(imgfile):
        img = f'<img width="300" src="boards/{name}.png">'
        bimg = f'<img align="right" width="400" src="{name}.png">'
    output.append(f"| {name} | {family} | {ftype} | {speed:0.2f}Mhz | {toolchain} | {description} | {img} |")

    boutput = []
    boutput.append(f"# {name}")
    boutput.append(bimg)
    boutput.append(description)
    boutput.append("")
    boutput.append("| Name | Value |")
    boutput.append("| --- | --- |")
    boutput.append(f"| Family | {family} |")
    boutput.append(f"| Type | {ftype} |")
    boutput.append(f"| Clock | {speed} |")
    boutput.append(f"| Toolchain | {toolchain} |")
    boutput.append("")

    boutput.append("## Slots")
    for slot in bdata.get("slots", []):
        boutput.append(f"### {slot['name']}")
        boutput.append(f"{slot.get('comment', '')}")
        boutput.append("")
        boutput.append("| Name | Pin | Direction |")
        boutput.append("| --- | --- | --- |")
        for pin_name, pin_data in slot.get("pins", {}).items():
            boutput.append(f"| {pin_name} | {pin_data['pin']} | {pin_data.get('direction', '')} |")
        boutput.append("")
    boutput.append("")
    boutput.append("")

    mdfile = bpath.replace(".json", ".md")
    open(mdfile, "w").write("\n".join(boutput))



output.append("")
open("riocore/plugins/fpga/BOARDS.md", "w").write("\n".join(output))

print("# TOOLCHAINS")
output = []
output.append("# TOOLCHAINS")
output.append("| Name | Info |")
output.append("| --- | --- |")
for ppath in sorted(glob.glob(os.path.join("riocore", "plugins", "fpga", "generator", "toolchains", "*", "toolchain.py"))):
    toolchain_name = os.path.basename(os.path.dirname(ppath))
    # print(toolchain_name)
    toolchain = importlib.import_module(".toolchain", f"riocore.plugins.fpga.generator.toolchains.{toolchain_name}")
    info = toolchain.Toolchain.info()
    if info:
        url = info.get("url", "")
        infotext = info.get("info", "")
        description = info.get("description", "")
        install = info.get("install", "")
        output.append(f"| [{toolchain_name}]({toolchain_name}/README.md) | {infotext} |")

        toutput = []
        toutput.append(f"# {toolchain_name}")
        toutput.append(f"**{infotext}**")
        toutput.append("")
        if url:
            toutput.append(f"* URL: [{url}]({url})")
            toutput.append("")

        if hasattr(toolchain.Toolchain, "pll"):
            toutput.append("* PLL: can generate PLL for some types")

        if description:
            toutput.append(f"{description}")
            toutput.append("")

        if install:
            toutput.append("")
            toutput.append("## Installation")
            toutput.append(f"{install}")
            toutput.append("")

        toutput.append("")
        open(os.path.join("riocore", "plugins", "fpga", "generator", "toolchains", toolchain_name, "README.md"), "w").write("\n".join(toutput))

output.append("")
open("riocore/plugins/fpga/generator/toolchains/README.md", "w").write("\n".join(output))


print("# MODIFIERS")
output = []
output.append("# MODIFIERS")
output.append("you can modify each input and output pin of the FPGA with an modifier pipeline")
output.append("")
output.append("```mermaid")
output.append("graph LR;")
output.append("    Input-Signal-->Modifier1;")
output.append("    Modifier1-->Modifier2;")
output.append("    Modifier2-->Modifier...;")
output.append("    Modifier...-->Output-Signal;")
output.append("```")
output.append("")


for name, data in Modifiers().info().items():
    # print(name, data)
    info = data.get("info", "")
    title = data.get("title", name.title())
    options = data.get("options")
    output.append(f"## {title}")

    if os.path.isfile(f"doc/images/mod_{name}.png"):
        output.append(f'<img align="right" width="300" src="images/mod_{name}.png">')

    output.append(info)
    output.append("")
    if options:
        output.append("**Options:**")
        output.append("| Name | Type | Default | Info |")
        output.append("| --- | --- | --- | --- |")
        for key, option in options.items():
            title = option.get("title", key.title())
            default = option.get("default", "")
            otype = option.get("type", "")
            oinfo = option.get("help_text", "")
            if inspect.isclass(otype):
                otype = otype.__name__
            output.append(f"| {title} | {otype!s} | {default} | {oinfo} |")
        output.append("")

output.append("")


open("doc/MODIFIERS.md", "w").write("\n".join(output))
