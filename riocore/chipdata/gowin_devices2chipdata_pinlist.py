import glob
import json

mapping = {}

csv = open("/opt/gowin/IDE/data/device/device_info.csv").read()

for line in csv.split("\n"):
    if not line:
        continue
    cols = line.split(",")
    print(cols[1], cols[3], cols[6])
    mtype = cols[3]
    mapping[cols[1]] = (mtype, cols[6])

    output = {}
    output[mtype] = {}

    for filename in glob.glob(f"/opt/gowin/IDE/data/device/{mtype}/*.json"):
        pkg = filename.split("/")[-1].split(".")[0]
        output[mtype][pkg] = {}

        with open(filename, "rb") as f:
            data = json.load(f)
            for pindata in data["PIN_DATA"]:
                if pindata["TYPE"] == "I/O":
                    pin = pindata["INDEX"]
                    comment = []
                    for key in ["NAME", "BANK", "CFG", "PAIR", "TRUELVDS"]:
                        if key in pindata:
                            value = pindata[key]
                            comment.append(f"{key}: {value}")

                    output[mtype][pkg][pin] = {
                        "comment": ", ".join(comment),
                        "source": filename,
                    }

        open(f"riocore/chipdata/{mtype}.json", "w").write(json.dumps(output, indent=4))


# print(json.dumps(output, indent=4))

print(mapping)
