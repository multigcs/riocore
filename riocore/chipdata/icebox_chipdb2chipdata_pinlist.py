#!/usr/bin/python
#
#


import json

packages = {}

for chip in ["1k", "384", "5k", "8k", "lm4k", "u4k"]:
    source = open(f"/opt/oss-cad-suite/share/icebox/chipdb-{chip}.txt").read()

    packages[chip] = {}

    package = ""
    for line in source.split("\n"):
        if line.startswith(".pins "):
            package = line.split()[1]
            packages[chip][package] = {}
        elif line.startswith("."):
            package = ""
        elif package and line:
            pinname = line.split()[0]
            packages[chip][package][pinname] = {"source": f"icebox/chipdb-{chip}.txt"}


print(json.dumps(packages, indent=4))
