import json

config = {
    "name": "EP4CE6E22C8",
    "description": "EP4CE6E22C8 devboard",
    "url": "",
    "toolchain": "quartus",
    "family": "Cyclone IV E",
    "type": "EP4CE6E22C8",
    "package": "",
    "clock": {"speed": "50000000", "pin": "PIN_24"},
    "slots": [
        {"name": "TOP", "comment": "", "default": "", "pins": {}},
        {"name": "BOTTOM", "comment": "", "default": "", "pins": {}},
        {"name": "RIGHT", "comment": "", "default": "", "pins": {}},
        {
            "name": "LED",
            "comment": "",
            "default": "",
            "pins": {
                "D1": {"pin": "PIN_1", "rotate": True, "pos": [255, 123], "direction": "output"},
                "D2": {"pin": "PIN_2", "rotate": True, "pos": [255, 143], "direction": "output"},
                "D3": {"pin": "PIN_3", "rotate": True, "pos": [255, 163], "direction": "output"},
                "D4": {"pin": "PIN_7", "rotate": True, "pos": [255, 183], "direction": "output"},
                "D5": {"pin": "PIN_11", "rotate": True, "pos": [255, 203], "direction": "output"},
            },
        },
        {
            "name": "BTN",
            "comment": "",
            "default": "",
            "pins": {
                "B1": {"pin": "114", "pos": [718, 64], "direction": "input"},
                "B2": {"pin": "89", "pos": [718, 159], "direction": "input"},
                "B3": {"pin": "88", "comment": "RESET", "pos": [721, 217], "direction": "input"},
                "B4": {"pin": "80", "pos": [718, 275], "direction": "input"},
                "B5": {"pin": "73", "pos": [718, 369], "direction": "input"},
            },
        },
    ],
}


pins = [
    "144",
    "142",
    "138",
    "136",
    "133",
    "129",
    "127",
    "125",
    "121",
    "119",
    "113",
    "111",
    "143",
    "141",
    "137",
    "135",
    "132",
    "128",
    "126",
    "124",
    "120",
    "115",
    "112",
    "110",
]

for n, pin in enumerate(pins):
    pname = f"P{n}"
    px = 280 + n * 22
    if n < 12:
        py = 14
    else:
        py = 36
        px -= 12 * 22
    config["slots"][0]["pins"][pname] = {"pin": f"PIN_{pin}", "rotate": True, "pos": [px, py], "direction": "output"}


pins = [
    "38",
    "42",
    "44",
    "49",
    "51",
    "53",
    "55",
    "59",
    "64",
    "66",
    "68",
    "70",
    "72",
    "39",
    "43",
    "46",
    "50",
    "52",
    "54",
    "58",
    "60",
    "65",
    "67",
    "69",
    "71",
]

for n, pin in enumerate(pins):
    pname = f"P{n}"
    px = 280 + n * 22
    if n < 13:
        py = 402
    else:
        py = 424
        px -= 13 * 22
    config["slots"][1]["pins"][pname] = {"pin": f"PIN_{pin}", "rotate": True, "pos": [px, py], "direction": "output"}


pins = [
    "106",
    "104",
    "101",
    "99",
    "86",
    "83",
    "28",
    "31",
    "33",
    "",
    "105",
    "103",
    "100",
    "98",
    "85",
    "77",
    "76",
    "30",
    "32",
    "34",
]

for n, pin in enumerate(pins):
    if not pin:
        continue
    pname = f"P{n}"
    py = 94 + n * 22
    if n < 10:
        px = 677
    else:
        px = 654
        py -= 10 * 22
    config["slots"][2]["pins"][pname] = {"pin": f"PIN_{pin}", "rotate": True, "pos": [px, py], "direction": "output"}


print(json.dumps(config, indent=4))
