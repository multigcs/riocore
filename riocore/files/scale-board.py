import json
import os
import subprocess
import sys

btype = "fpga"
# btype = "mesa"
# btype = "ninja"
btype = "breakout"

board_name = sys.argv[1]
json_file = f"riocore/plugins/{btype}/boards/{board_name}.json"
png_file = f"riocore/plugins/{btype}/boards/{board_name}.png"

xscale = float(sys.argv[2])
yscale = float(sys.argv[3])

jdata = json.loads(open(json_file, "r").read())

if btype == "fpga":
    for slot in jdata["slots"]:
        for pin, data in slot["pins"].items():
            pos = data.get("pos")
            if pos:
                print(pin, pos)
                data["pos"] = [int(pos[0] * xscale), int(pos[1] * yscale)]
elif btype == "breakout":
    for slot in jdata["slots"]:
        for pin, data in slot["pins"].items():
            pos = data.get("pos")
            if pos:
                print(pin, pos)
                data["pos"] = [int(pos[0] * xscale), int(pos[1] * yscale)]
    for pin, data in jdata.get("main", {}).items():
        pos = data.get("pos")
        if pos:
            print(pin, pos)
            data["pos"] = [int(pos[0] * xscale), int(pos[1] * yscale)]
elif btype == "ninja":
    for pin, data in jdata.items():
        pos = data.get("pos")
        if pos:
            print(pin, pos)
            data["pos"] = [int(pos[0] * xscale), int(pos[1] * yscale)]
else:
    for pin, data in jdata["pins"].items():
        pos = data.get("pos")
        if pos:
            print(pin, pos)
            data["pos"] = [int(pos[0] * xscale), int(pos[1] * yscale)]

res = subprocess.check_output(["identify", png_file]).decode()
size = res.split()[2].split("x")
size_x = int(size[0])
size_y = int(size[1])
cmd = f"convert -scale {int(size_x * xscale)}x {png_file} {png_file}"
print(cmd)
os.system(cmd)
print(json.dumps(jdata, indent=2))
open(json_file, "w").write(json.dumps(jdata, indent=2))
