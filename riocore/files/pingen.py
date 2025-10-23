
import sys
import json


names = sys.argv[1]
xoff = int(sys.argv[2])
yoff = int(sys.argv[3])
xdiff = int(sys.argv[4])
ydiff = int(sys.argv[5])

jdata = {
    "pins": {
    }
}

for name in names.split():
    print(name)
    jdata["pins"][name] = {
        "pin": name,
        "pos": [
            xoff,
            yoff,
        ],
        "direction": "all"
    }
    xoff += xdiff
    yoff += ydiff


data = json.dumps(jdata, indent=4) 

print(data)




