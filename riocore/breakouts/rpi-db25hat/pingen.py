import json

config = {
    "comment": "rpi-db25hat",
    "main": {},
    "slots": [
        {
            "name": "DB25",
            "comment": "",
            "default": "",
            "pins": {
                "P1": {"pin": "P1", "pos": [212, 771], "direction": "input"},
                "P2": {"pin": "P1", "pos": [212, 771], "direction": "input"},
                "P3": {"pin": "P1", "pos": [212, 771], "direction": "input"},
                "P4": {"pin": "P1", "pos": [212, 771], "direction": "input"},
                "P5": {"pin": "P1", "pos": [212, 771], "direction": "input"},
                "P6": {"pin": "P1", "pos": [212, 771], "direction": "input"},
                "P7": {"pin": "P1", "pos": [212, 771], "direction": "input"},
                "P8": {"pin": "P1", "pos": [212, 771], "direction": "input"},
                "P9": {"pin": "P1", "pos": [212, 771], "direction": "input"},
                "P10": {"pin": "P1", "pos": [212, 771], "direction": "input"},
                "P11": {"pin": "P1", "pos": [212, 771], "direction": "input"},
                "P12": {"pin": "P1", "pos": [212, 771], "direction": "input"},
                "P13": {"pin": "P1", "pos": [212, 771], "direction": "input"},
                "P14": {"pin": "P1", "pos": [212, 771], "direction": "input"},
                "P15": {"pin": "P1", "pos": [212, 771], "direction": "input"},
                "P16": {"pin": "P1", "pos": [212, 771], "direction": "input"},
                "P17": {"pin": "P1", "pos": [212, 771], "direction": "input"},
            },
        }
    ],
}

mapping = {
    "P1": ("PWM", "P12"),
    "P2": ("XSTEP", "P21"),
    "P3": ("XDIR", "P19"),
    "P4": ("YSTEP", "P23"),
    "P5": ("YDIR", "P29"),
    "P6": ("ZSTEP", "P31"),
    "P7": ("ZDIR", "P35"),
    "P8": ("ASTEP", "P11"),
    "P9": ("ADIR", "P16"),
    "P10": ("LIMIT1", "P22"),
    "P11": ("LIMIT2", "P24"),
    "P12": ("LIMIT3", "P26"),
    "P13": ("LIMIT4", "P32"),
    "P14": ("ALLEN", "P37"),
    "P15": ("LIMIT5", "P33"),
    "P16": ("BSTEP", "P13"),
    "P17": ("BDIR", "P24"),
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
for n, pin in enumerate(pins, 1):
    if not pin:
        continue
    pname = f"P{n}"

    px = 128
    py = n // 2 * 25.3 + 82
    if si == 1:
        px += 25
        py -= 25.3
    if pin.startswith("GP"):
        config["main"][pname] = {"pos": [170 - px, 658 - py]}

    si = 1 - si


for n in range(17):
    pname = f"P{n + 1}"

    px = 528
    py = n * 22 + 82
    if n > 12:
        px += 22
        py -= 13 * 22

    direction = "output"
    if mapping[pname][0].startswith("LIMIT"):
        direction = "input"
    config["slots"][0]["pins"][pname] = {"pin": mapping[pname][1], "comment": mapping[pname][0], "pos": [1120 - px, 540 - py], "direction": direction}

print(json.dumps(config, indent=4))
