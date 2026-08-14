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

if filename.startswith("riocore/files/images/"):
    print("image rescale only")
    png_file = filename
    res = subprocess.check_output(["identify", filename]).decode()
    size = res.split()[2].split("x")
    size_x = int(size[0])
    size_y = int(size[1])
    cmd = f"convert -scale {int(size_x * xscale)}x {filename} {filename}"
    print(cmd)
    if run:
        os.system(cmd)
    exit(0)

board_name = filename.split("/")[4].replace(".png", "").replace(".json", "")
btype = filename.split("/")[2]


if btype == "i2c_device":
    print("image rescale only")
    res = subprocess.check_output(["identify", filename]).decode()
    size = res.split()[2].split("x")
    size_x = int(size[0])
    size_y = int(size[1])
    cmd = f"convert -scale {int(size_x * xscale)}x {filename} {filename}"
    print(cmd)
    if run:
        os.system(cmd)
    exit(0)


if btype == "ethercat":
    json_file = f"riocore/plugins/{btype}/modules/{board_name}.json"
    png_file = f"riocore/plugins/{btype}/modules/{board_name}.png"
else:
    json_file = f"riocore/plugins/{btype}/boards/{board_name}.json"
    png_file = f"riocore/plugins/{btype}/boards/{board_name}.png"


jdata = json.loads(open(json_file, "r").read())

if btype == "fpga":
    for slot in jdata.get("slots", []):
        for pin, data in slot["pins"].items():
            pos = data.get("pos")
            if pos:
                print(pin, pos)
                data["pos"] = [int(pos[0] * xscale), int(pos[1] * yscale)]

    for slot in jdata.get("plugins", []):
        for pin, data in slot["pins"].items():
            pos = data.get("pos")
            if pos:
                print(pin, pos)
                data["pos"] = [int(pos[0] * xscale), int(pos[1] * yscale)]


elif btype == "breakout":
    for slot in jdata.get("slots", []):
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

elif btype == "ninja":
    for pin, data in jdata["pins"].items():
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
if run:
    os.system(cmd)
    print(json.dumps(jdata, indent=2))
    open(json_file, "w").write(json.dumps(jdata, indent=2))
