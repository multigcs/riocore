#!/usr/bin/env python3
#
#

import json
import subprocess


def wizard():
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
            {"type": "ethercat", "node_type": "Master", "uid": "ec0", "pos": [0.0, 50.0]},
        ],
    }

    last = "ec0"
    koppler = None
    pos_x = 150.0
    for slave_id, slave_data in ethercat[0].items():
        vid = slave_data.get("identity", {}).get("Vendor Id")
        # pid = slave_data.get("identity", {}).get("Product code")
        protocols = slave_data.get("mailboxes", {}).get("Supported protocols")
        # group = slave_data.get("general", {}).get("Group")
        dev_name = slave_data.get("general", {}).get("Device name")
        conn = slave_data.get("ports", {}).get("0", [""])[0]
        # print(slave_id, vid, pid, dev_name, protocols, conn)
        if vid == "0x00000002" and dev_name.split()[0] == "EK1100":
            node_type = dev_name.split()[0].lower()
            uid = f"ec{slave_id + 1}"
            koppler = {"type": "ethercat", "node_type": node_type, "uid": uid, "pos": [pos_x, 20.0], "pins": {"BUS:in": {"pin": f"{last}:BUS:out"}}, "modules": "", "sub": {}}
            pos_x += 200.0
            config["plugins"].append(koppler)
            last = uid

        elif koppler and conn == "EBUS":
            node_type = dev_name.split()[0].lower()
            uid = f"ec{slave_id + 1}"
            sub_n = len(koppler["sub"])

            koppler["modules"] += node_type + " "
            koppler["sub"][str(sub_n)] = {"type": "ethercat", "node_type": node_type, "uid": uid, "rpos": [pos_x, 0.0]}
            pos_x += 70

        else:
            koppler = None
            if protocols and "coe" in protocols.lower():
                uid = f"ec{slave_id + 1}"
                config["plugins"].append({"type": "ethercat", "node_type": "Servo/Stepper", "uid": uid, "is_joint": True, "image": "ethercatservo", "pos": [pos_x, -30.0], "pins": {"BUS:in": {"pin": f"{last}:BUS:out"}}})
                pos_x += 180.0
                last = uid

    # print(json.dumps(config, indent=4))
    return config


if __name__ == "__main__":
    print(json.dumps(wizard(), indent=4))
