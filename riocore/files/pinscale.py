import sys
import json


json_file = sys.argv[1]
slot_selection = sys.argv[2]
xscale = float(sys.argv[3])
yscale = float(sys.argv[4])

jdata = json.loads(open(json_file, "r").read())

if slot_selection == "main":
    for pin, pdata in jdata[slot_selection].items():
        # pdata["pos"][0] += xoff
        # pdata["pos"][1] += yoff
        pass

else:
    found = False
    min_x = 999999999999
    min_y = 999999999999
    for slot in jdata["slots"]:
        if slot_selection == slot["name"]:
            found = True
            for pin, pdata in slot["pins"].items():
                min_x = min(min_x, pdata["pos"][0])
                min_y = min(min_x, pdata["pos"][1])

    for slot in jdata["slots"]:
        if slot_selection == slot["name"]:
            for pin, pdata in slot["pins"].items():
                pdata["pos"][0] = (pdata["pos"][0] - min_x) * xscale + min_x
                pdata["pos"][1] = (pdata["pos"][1] - min_y) * yscale + min_y

    if not found:
        print(f"slot '{slot_selection}' not found")
        exit(0)


data = json.dumps(jdata, indent=4)

print(data)

open(json_file, "w").write(data)
