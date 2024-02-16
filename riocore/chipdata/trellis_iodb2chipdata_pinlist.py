#!/usr/bin/python
#
#


import json

packages = {}
for chip in ["LFE5U-12F", "LFE5U-45F", "LFE5UM-25F", "LFE5UM5G-25F", "LFE5UM5G-85F", "LFE5U-25F", "LFE5U-85F", "LFE5UM-45F", "LFE5UM5G-45F", "LFE5UM-85F"]:
    source = json.loads(open(f"/opt/oss-cad-suite/share/trellis/database/ECP5/{chip}/iodb.json").read())
    packages[chip] = {}
    for package in source["packages"]:
        packages[chip][package] = {}
        for pin in source["packages"][package]:
            packages[chip][package][pin] = {"source": f"trellis/database/ECP5/{chip}/iodb.json"}

print(json.dumps(packages, indent=4))
