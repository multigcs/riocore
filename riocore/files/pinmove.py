
import sys
import json


json_file = sys.argv[1]
section = sys.argv[2]
xoff = int(sys.argv[3])
yoff = int(sys.argv[4])

jdata = json.loads(open(json_file, "r").read())

if section == "main":
    for pin, pdata in jdata[section].items():
        pdata["pos"][0] += xoff
        pdata["pos"][1] += yoff

else:
    found = False
    for slot in jdata["slots"]:
        if section == slot["name"]:
            found = True
            for pin, pdata in slot["pins"].items():
                pdata["pos"][0] += xoff
                pdata["pos"][1] += yoff

    if not found:
        print(f"slot '{section}' not found")
        exit(0)


data = json.dumps(jdata, indent=4) 

print(data)

open(json_file, "w").write(data)


