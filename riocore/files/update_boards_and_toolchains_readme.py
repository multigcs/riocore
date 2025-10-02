#!/usr/bin/env python3
#
#

import glob
import os
import json
import importlib
import inspect
from riocore.modifiers import Modifiers


examples = {}
for cpath in sorted(glob.glob(os.path.join("riocore", "configs", "*", "config.json"))):
    cjdata = open(cpath, "r").read()
    cdata = json.loads(cjdata)
    boardcfg = cdata.get("boardcfg")
    if boardcfg not in examples:
        examples[boardcfg] = []
    examples[boardcfg].append(cpath)


print("# BOARDS")
index = []

index.append("# BOARDS")
index.append("| Name | Info | FPGA | Toolchains | Image |")
index.append("| --- | --- | --- |  --- | :---: |")

for board in sorted(glob.glob(os.path.join("riocore", "boards", "*"))):
    board_path = os.path.join(board, "board.json")
    if not os.path.isfile(board_path):
        continue

    print(board_path)

    name = board.split(os.sep)[-1]

    jdata = open(board_path, "r").read()
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
            if key == "toolchain":
                if "toolchains" in data:
                    toolchains = []
                    for toolchain in data["toolchains"]:
                        if toolchain == data[key]:
                            continue
                        toolchains.append(f"[{toolchain}](../../generator/toolchains/{toolchain}/README.md)")
                    readme.append(f"* {key.title()}: [{data[key]}](../../generator/toolchains/{data[key]}/README.md) ({', '.join(toolchains)})")
                else:
                    readme.append(f"* {key.title()}: [{data[key]}](../../generator/toolchains/{data[key]}/README.md)")
            else:
                readme.append(f"* {key.title()}: {data[key]}")

    if "clock" in data:
        speed_mhz = float(data["clock"]["speed"]) / 1000000
        if "osc" in data["clock"]:
            osc_mhz = float(data["clock"]["osc"]) / 1000000
            readme.append(f"* Clock: {osc_mhz:0.3f}Mhz -> PLL -> {speed_mhz:0.3f}Mhz (Pin:{data['clock'].get('pin')})")
        else:
            readme.append(f"* Clock: {speed_mhz:0.3f}Mhz (Pin:{data['clock'].get('pin')})")

    example_links = []
    for example in examples.get(name, []):
        example_name = example.split(os.sep)[-2]
        example_json = example.split(os.sep)[-1]
        example_links.append(f"[{example_name}](../../configs/{example_name})")

    if example_links:
        readme.append(f"* Example-Configs: {', '.join(example_links)}")

    readme.append("")

    fpga_type = data.get("type", "")
    fpga_family = data.get("family", "")

    toolchains = []
    if "toolchains" in data:
        for toolchain in data["toolchains"]:
            toolchains.append(f"[{toolchain}](../generator/toolchains/{toolchain}/README.md)")
    else:
        toolchain = data.get("toolchain", "")
        toolchains.append(f"[{toolchain}](../generator/toolchains/{toolchain}/README.md)")

    if os.path.isfile(os.path.join(board, "board.png")):
        readme.append("![board.png](board.png)")
        readme.append("")
        index.append(f'| [{name}]({name}/README.md) | {description} | {fpga_family} / {fpga_type} | {", ".join(toolchains)} | <img src="{name}/board.png" height="48"> |')
    else:
        index.append(f"| [{name}]({name}/README.md) | {description} | {fpga_family} / {fpga_type} | {', '.join(toolchains)} | |")

    readme.append("")

    open(f"{board}/README.md", "w").write("\n".join(readme))

index.append("")
open("riocore/boards/README.md", "w").write("\n".join(index))

print("# TOOLCHAINS")
output = []
output.append("# TOOLCHAINS")
output.append("| Name | Info |")
output.append("| --- | --- |")

for ppath in sorted(glob.glob(os.path.join("riocore", "generator", "toolchains", "*", "toolchain.py"))):
    toolchain_name = os.path.basename(os.path.dirname(ppath))
    print(toolchain_name)
    toolchain = importlib.import_module(".toolchain", f"riocore.generator.toolchains.{toolchain_name}")
    info = toolchain.Toolchain.info(None)
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
        open(os.path.join("riocore", "generator", "toolchains", toolchain_name, "README.md"), "w").write("\n".join(toutput))


output.append("")


open("riocore/generator/toolchains/README.md", "w").write("\n".join(output))


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
    print(name, data)
    info = data.get("info", "")
    title = data.get("title", name.title())
    options = data.get("options")
    output.append(f"## {title}")
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
            output.append(f"| {title} | {str(otype)} | {default} | {oinfo} |")
        output.append("")

output.append("")


open("doc/MODIFIERS.md", "w").write("\n".join(output))
