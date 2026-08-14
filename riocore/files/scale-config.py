import json
import os
import subprocess
import sys

run = False
filename = sys.argv[1]
xscale = float(sys.argv[2])
yscale = float(sys.argv[3])
if len(sys.argv) == 5 and sys.argv[4] == "run":
    print("run")
    run = True
else:
    print("DEBUG_MODE")


jdata = json.loads(open(filename, "r").read())

for plugin in jdata.get("plugins", []):
    pos = plugin.get("pos")
    if pos:
        pos[0] *= xscale
        pos[1] *= xscale
        print(pos)

    if "flow" in jdata:
        del jdata["flow"]


print(json.dumps(jdata, indent=2))
if run:
    open(filename, "w").write(json.dumps(jdata, indent=2))
