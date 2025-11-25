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
            output.append(f"| {title} | {otype!s} | {default} | {oinfo} |")
        output.append("")

output.append("")


open("doc/MODIFIERS.md", "w").write("\n".join(output))
