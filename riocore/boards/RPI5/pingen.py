import json

config = {
    "name": "RPI5",
    "description": "RPI5",
    "comment": "",
    "url": "",
    "type": "gpio",
    "slots": [
        {"name": "GPIO", "comment": "", "default": "", "pins": {}},
    ],
}


pins = (
    "3V3",
    "5V",
    "GPIO2",
    "5V",
    "GPIO3",
    "GND",
    "GPIO4",
    "GPIO14",
    "GND",
    "GPIO15",
    "GPIO17",
    "GPIO18",
    "GPIO27",
    "GND",
    "GPIO22",
    "GPIO23",
    "3V3",
    "GPIO24",
    "GPIO10",
    "GND",
    "GPIO9",
    "GPIO25",
    "GPIO11",
    "GPIO8",
    "GND",
    "GPIO7",
    "_GPIO0",
    "_GPIO1",
    "GPIO5",
    "GND",
    "GPIO6",
    "GPIO12",
    "GPIO13",
    "GND",
    "GPIO19",
    "GPIO16",
    "GPIO26",
    "GPIO20",
    "GND",
    "GPIO21",
)

si = 0
for n, pin in enumerate(pins):
    if not pin:
        continue
    pname = f"P{n}"

    px = 528
    if si == 1:
        px += 25

    py = n // 2 * 25.3 + 82
    if pin.startswith("GP"):
        config["slots"][0]["pins"][pname] = {"pin": f"{pin}", "rotate": True, "pos": [px, py], "direction": "all"}

    si = 1 - si


print(json.dumps(config, indent=4))
