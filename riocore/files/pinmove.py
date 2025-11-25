import json
import sys

json_file = sys.argv[1]
slot_selection = sys.argv[2]
xoff = int(sys.argv[3])
yoff = int(sys.argv[4])

jdata = json.loads(open(json_file).read())

if slot_selection == "main":
    for pin, pdata in jdata[slot_selection].items():
        pdata["pos"][0] += xoff
        pdata["pos"][1] += yoff

else:
    found = False
    for slot in jdata["slots"]:
        if slot_selection == slot["name"]:
            found = True
            for pin, pdata in slot["pins"].items():
                pdata["pos"][0] += xoff
                pdata["pos"][1] += yoff

    if not found:
        print(f"slot '{slot_selection}' not found")
        exit(0)


data = json.dumps(jdata, indent=4)

print(data)

open(json_file, "w").write(data)
