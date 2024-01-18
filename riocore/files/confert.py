import json
import os
import sys

plugin_mapping = {
    "din_bit": "bitin",
    "dout_bit": "bitout",
    "joint_pwmdir": "pwmout",
    "joint_rcservo": "rcservo",
    "joint_stepper": "stepdir",
    "joint_stepper4pins": "stepper",
    "vin_frequency": "freqin",
    "vin_ir": "irin",
    "vin_pwm": "pwmin",
    "vin_pwmcounter": "pwmin",
    "vin_tlc549c": "tlc549c",
    "vout_7seg": "dis7seg",
    "vout_frequency": "freqout",
    "vout_pwm": "pwmout",
    "vout_rcservo": "rcservo",
    "uart": "uart",
    "spi": "spi",
    "w5500": "w5500",
    "vin_pulsecounter": "counter",
    "vin_ads1115": "ads1115",
    "vin_quadencoderz": "quadencoderz",
    "vin_quadencoder": "quadencoder",
    "vout_sine": "sine",
    "vout_udpoti": "udpoti",
    "vin_ds18b20": "ds18b20",
    "udp_tangprimer20k": "udp_tangprimer20k",
    "shiftreg": "shiftreg",
}

pin_mapping = {
    "udp_tangprimer20k": {
        "phyrst": "phyrst",
        "netrmii_txd_1": "txd_1",
        "netrmii_txd_0": "txd_0",
        "netrmii_txen": "txen",
        "netrmii_mdc": "mdc",
        "netrmii_rxd_1": "rxd_1",
        "netrmii_rxd_0": "rxd_0",
        "netrmii_rx_crs": "rx_crs",
        "netrmii_clk50m": "clk50m",
        "netrmii_mdio": "mdio",
    },
    "vout_udpoti": {
        "updown": "updown",
        "incr": "increment",
    },
    "uart": {
        "RX": "rx",
        "TX": "tx",
    },
    "vin_ds18b20": {
        "data": "one_wire",
    },
    "shiftreg": {"out": "out", "in": "in", "clock": "sclk", "load": "load"},
    "w5500": {
        "MOSI": "mosi",
        "MISO": "miso",
        "SCK": "sclk",
        "SEL": "sel",
    },
    "spi": {
        "MOSI": "mosi",
        "MISO": "miso",
        "SCK": "sclk",
        "SEL": "sel",
    },
    "vin_ads1115": {
        "scl": "scl",
        "sda": "sda",
    },
    "vin_quadencoderz": {
        "a": "a",
        "b": "b",
        "z": "z",
    },
    "vin_quadencoder": {
        "a": "a",
        "b": "b",
    },
    "vin_pulsecounter": {
        "up": "up",
        "down": "down",
        "reset": "reset",
    },
    "vin_pwmcounter": {
        "pin": "pwm",
    },
    "din_bit": {
        "pin": "bit",
    },
    "dout_bit": {
        "pin": "bit",
    },
    "joint_pwmdir": {
        "pin": "bit",
        "pwm": "pwm",
        "dir": "dir",
    },
    "joint_rcservo": {
        "pin": "bit",
        "pwm": "pwm",
    },
    "joint_stepper": {
        "pin": "bit",
        "step": "step",
        "dir": "dir",
        "enable": "enable",
    },
    "vin_frequency": {
        "pin": "freq",
    },
    "vin_ir": {
        "pin": "ir",
        "ir": "ir",
    },
    "vin_pwm": {
        "pin": "pwm",
        "pwm": "pwm",
    },
    "vin_tlc549c": {
        "miso": "miso",
        "sclk": "sclk",
        "cs": "sel",
    },
    "vout_7seg": {
        "en1": "en1",
        "en2": "en2",
        "en3": "en3",
        "en4": "en4",
        "seg_a": "seg_a",
        "seg_b": "seg_b",
        "seg_c": "seg_c",
        "seg_d": "seg_d",
        "seg_e": "seg_e",
        "seg_f": "seg_f",
        "seg_g": "seg_g",
    },
    "vout_frequency": {
        "pin": "bit",
    },
    "vout_pwm": {
        "pwm": "pwm",
        "dir": "dir",
        "pin": "pwm",
    },
    "vout_rcservo": {
        "pin": "bit",
        "pwm": "pwm",
    },
}


data = json.loads(open(sys.argv[1], "r").read())

error = False

boardcfg = {}
if "boardcfg" in data:
    boardcfg = json.loads(open(f"riocore/boards/{data['boardcfg']}.json", "r").read())


pinmapping = {}
for slot in boardcfg.get("slots", []):
    slot_name = slot["name"]
    for pin_id, pin in slot["pins"].items():
        pin_name = f"{slot_name}:{pin_id}"
        pinmapping[pin] = pin_name

if "plugins" not in data:
    data["plugins"] = []

if data.get("interface", []):
    for interface in data.get("interface", []):
        data["plugins"].append(interface)
    del data["interface"]

if data.get("expansion", []):
    for interface in data.get("expansion", []):
        data["plugins"].append(interface)
    del data["expansion"]

fb_num = 0
for plugin in data["plugins"].copy():
    old_type = plugin["type"]

    if old_type.startswith("_"):
        continue

    if plugin["type"] not in plugin_mapping:
        print(f"missing plugin mapping for plugin {old_type}")
        error = True
    else:
        plugin["type"] = plugin_mapping[plugin["type"]]

    if old_type.startswith("joint_"):
        plugin["joint"] = True

    if "pin" in plugin:
        plugin["pins"] = {
            "pin": plugin["pin"],
        }
        del plugin["pin"]

    is_joint = plugin.get("joint")

    if is_joint:

        if "cl" in plugin:
            del plugin["cl"]

        enc_a = plugin.get("pins", {}).get("enc_a")
        enc_b = plugin.get("pins", {}).get("enc_b")
        if enc_a:
            print(plugin.get("pins", {}))
            del plugin["pins"]["enc_a"]
            del plugin["pins"]["enc_b"]

            plugin["feedback"] = f"feedback{fb_num}:position"
            data["plugins"].append(
                {
                    "name": f"feedback{fb_num}",
                    "type": "quadencoder",
                    "pins": {
                        "a": {
                            "pin": pinmapping.get(enc_a, enc_a),
                        },
                        "b": {
                            "pin": pinmapping.get(enc_b, enc_b),
                        },
                    },
                }
            )
            fb_num += 1

    if "pins" in plugin:
        new_pins = {}
        ok = True
        invert = plugin.get("invert", False)
        debounce = plugin.get("debounce", False)
        pullup = plugin.get("pullup", False)

        if invert:
            del plugin["invert"]
        if debounce:
            del plugin["debounce"]
        if pullup:
            del plugin["pullup"]

        if isinstance(plugin.get("pins"), list):
            print("ERROR pins is a list")
            continue
            exit(1)

        for pin_name, pin in plugin.get("pins", {}).items():
            old_pin_name = pin_name
            pin_name = pin_mapping.get(old_type, {}).get(old_pin_name)
            if not pin_name:
                ok = False
                print(f'missing pin mapping for plugin: {old_type:16s} pin: "{old_pin_name}": "{old_pin_name.lower()}",')
                error = True
                # break
            new_pins[pin_name] = {
                "pin": pinmapping.get(pin, pin),
            }
            if pullup:
                new_pins[pin_name]["pullup"] = True

            if invert or debounce:
                new_pins[pin_name]["modifier"] = []
                if invert:
                    new_pins[pin_name]["modifier"].append({"type": "invert"})
                if debounce:
                    new_pins[pin_name]["modifier"].append({"type": "debounce"})
        if ok:
            plugin["pins"] = new_pins


if not error:
    print(json.dumps(data, indent=2))

    # print("try to build")
    # open("/tmp/t.json", "w").write(json.dumps(data, indent=4))
    # os.system("python3 testme.py /tmp/t.json")
else:
    exit(1)
