#!/usr/bin/env python3
#
#

import glob
import os
import json
import importlib


print("# BOARDS")
index = []

index.append("# BOARDS")
index.append("| Name | Info | FPGA | Toolchains | Image |")
index.append("| --- | --- | --- |  --- | :---: |")

for board in sorted(glob.glob("riocore/boards/*")):
    if not os.path.isfile(f"{board}/board.json"):
        continue

    print(f"{board}/board.json")

    name = board.split("/")[-1]

    jdata = open(f"{board}/board.json", "r").read()
    data = json.loads(jdata)

    readme = []

    readme.append(f"# {name}")
    description = ""
    if "description" in data:
        description = data["description"]
        readme.append(f"**{description}**")
    readme.append("")

    if "comment" in data:
        comment = data["comment"]
        readme.append(comment)
        readme.append("")

    if "url" in data:
        readme.append(f"* URL: [{data['url']}]({data['url']})")

    for key in ("toolchain", "family", "type", "package", "flashcmd"):
        if key in data:
            if key == "toolchain" and "toolchains" in data:
                readme.append(f"* {key.title()}: {data[key]} ({', '.join(data['toolchains'])})")
            else:
                readme.append(f"* {key.title()}: {data[key]}")

    if "clock" in data:
        speed_mhz = float(data["clock"]["speed"]) / 1000000
        if "osc" in data["clock"]:
            osc_mhz = float(data["clock"]["osc"]) / 1000000
            readme.append(f"* Clock: {osc_mhz:0.3f}Mhz -> PLL -> {speed_mhz:0.3f}Mhz (Pin:{data['clock']['pin']})")
        else:
            readme.append(f"* Clock: {speed_mhz:0.3f}Mhz (Pin:{data['clock']['pin']})")

    readme.append("")

    fpga_type = data.get("type", "")
    fpga_family = data.get("family", "")
    toolchains = data.get("toolchains", [data.get("toolchain", "")])

    if os.path.isfile(f"{board}/board.png"):
        readme.append("![board.png](board.png)")
        readme.append("")
        index.append(f'| [{name}](riocore/boards/{name}/README.md) | {description} | {fpga_family} / {fpga_type} | {", ".join(toolchains)} | <img src="riocore/boards/{name}/board.png" height="48"> |')
    else:
        index.append(f"| [{name}](riocore/boards/{name}/README.md) | {description} | {fpga_family} / {fpga_type} | {', '.join(toolchains)} | |")

    readme.append("")

    open(f"{board}/README.md", "w").write("\n".join(readme))

index.append("")
open("BOARDS.md", "w").write("\n".join(index))

print("# TOOLCHAINS")
output = []
output.append("# TOOLCHAINS")
output.append("| Name | Info |")
output.append("| --- | --- |")

for ppath in sorted(glob.glob("riocore/generator/toolchains/*/toolchain.py")):
    toolchain_name = os.path.basename(os.path.dirname(ppath))
    print(toolchain_name)
    toolchain = importlib.import_module(".toolchain", f"riocore.generator.toolchains.{toolchain_name}")
    info = toolchain.Toolchain.info(None)
    if info:
        url = info.get("url", "")
        infotext = info.get("info", "")
        description = info.get("description", "")
        install = info.get("install", "")
        output.append(f"| [{toolchain_name}](riocore/generator/toolchains/{toolchain_name}/README.md) | {infotext} |")

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
        open(f"riocore/generator/toolchains/{toolchain_name}/README.md", "w").write("\n".join(toutput))


output.append("")


open("TOOLCHAINS.md", "w").write("\n".join(output))
