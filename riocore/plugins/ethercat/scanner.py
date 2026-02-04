#
# convert "https://multimedia.beckhoff.com/media/el1002_es1002__web_preview.png.webp" -crop 76x626+328+45 /tmp/el1002.png
# convert "https://multimedia.beckhoff.com/media/el2002_es2002__web_preview.png.webp" -crop 76x626+328+45 /tmp/el2002.png
# convert "https://multimedia.beckhoff.com/media/el4002_es4002__web_preview.png.webp" -crop 76x626+328+45 /tmp/el4002.png
# convert "https://multimedia.beckhoff.com/media/el9110_es9110__web_preview.png.webp" -crop 76x626+328+45 /tmp/el9110.png
# convert "https://multimedia.beckhoff.com/media/el7411__web_preview.png.webp" -crop 152x626+295+45 /tmp/el7411.png
#


import json
import subprocess

ethercat = {}
output = subprocess.check_output(["ethercat", "slaves", "-v"])
if not output:
    exit(1)


master = None
slave = None
section = None
for line in output.decode().split("\n"):
    # print("#", line)
    if line.startswith("=== Master"):
        master = int(line.split()[2].strip(","))
        slave = int(line.split()[4])
        if master not in ethercat:
            ethercat[master] = {}
        if slave not in ethercat[master]:
            ethercat[master][slave] = {}

    elif line and line[0] != " ":
        if line.startswith("Port "):
            section = "ports"
        else:
            section = line.strip(":").lower()
        ethercat[master][slave][section] = {}

    elif section == "ports":
        name = line.split()[0].strip()
        value = line.strip().split(" ", 1)[1].strip().split()
        ethercat[master][slave][section][name] = value

    elif section is not None and ":" in line:
        name = line.split(":")[0].strip()
        value = line.split(":", 1)[1].strip()
        ethercat[master][slave][section][name] = value

# print(json.dumps(ethercat, indent=4))

config = {
    "name": "Ethercat",
    "plugins": [
        {"type": "ethercat", "node_type": "Master", "uid": "ec0", "pos": [20.0, 50.0]},
    ],
}

last = "ec0"
koppler = None
for slave_id, slave_data in ethercat[0].items():
    vid = slave_data.get("identity", {}).get("Vendor Id")
    pid = slave_data.get("identity", {}).get("Product code")
    protocols = slave_data.get("mailboxes", {}).get("Supported protocols")
    group = slave_data.get("general", {}).get("Group")
    dev_name = slave_data.get("general", {}).get("Device name")
    conn = slave_data.get("ports", {}).get("0", [""])[0]

    # print(slave_id, vid, pid, dev_name, protocols, conn)

    if vid == "0x00000002" and dev_name.split()[0] == "EK1100":
        node_type = dev_name.split()[0].lower()
        uid = f"ec{slave_id + 1}"
        koppler = {"type": "ethercat", "node_type": node_type, "uid": uid, "pos": [390.0, 20.0], "pins": {"BUS:in": {"pin": f"{last}:BUS:out"}}, "modules": "", "sub": {}}
        config["plugins"].append(koppler)
        last = uid

    elif koppler and conn == "EBUS":
        node_type = dev_name.split()[0].lower()
        uid = f"ec{slave_id + 1}"
        sub_n = len(koppler["sub"])

        koppler["modules"] += node_type + " "
        # """
        koppler["sub"][str(sub_n)] = {"type": "ethercat", "node_type": node_type, "uid": uid, "rpos": [263, 0.0]}
        # """

    else:
        koppler = None

        if protocols and "coe" in protocols.lower():
            uid = f"ec{slave_id + 1}"
            config["plugins"].append({"type": "ethercat", "node_type": "Servo/Stepper", "uid": uid, "is_joint": True, "image": "ethercatservo", "pos": [180.0, -30.0], "pins": {"BUS:in": {"pin": f"{last}:BUS:out"}}})
            last = uid

print(json.dumps(config, indent=4))
# print(json.dumps(ec[0], indent=4))
