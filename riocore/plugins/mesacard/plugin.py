import os

from riocore.plugins import PluginBase


class Plugin(PluginBase):
    def setup(self):
        self.NAME = "mesacard"
        self.COMPONENT = "mesacard"
        self.INFO = "mesacard"
        self.DESCRIPTION = "mesacard"
        self.KEYWORDS = "mesacard gpio"
        self.TYPE = "base"
        self.IMAGE_SHOW = True
        self.PLUGIN_TYPE = "gpio"
        self.ORIGIN = ""
        self.OPTIONS = {
            "cardtype": {
                "default": "7c81_5abobx3d",
                "type": "select",
                "options": [
                    "7c81_5abobx2d",
                    "7c81_5abobx3d",
                    "7i92_5ABOBx2D",
                ],
                "description": "card configuration",
            },
        }
        self.SIGNALS = {}
        self.PINDEFAULTS = {}

        pinpos = {
            "7c81": {
                "P1": {
                    "pins": {
                        "IO0": {"pin": "P119", "pos": [115, 59]},
                        "IO2": {"pin": "P117", "pos": [134, 59]},
                        "IO4": {"pin": "P115", "pos": [153, 59]},
                        "IO6": {"pin": "P112", "pos": [172, 59]},
                        "IO8": {"pin": "P105", "pos": [191, 59]},
                        "IO9": {"pin": "P104", "pos": [210, 59]},
                        "IO10": {"pin": "P102", "pos": [229, 59]},
                        "IO11": {"pin": "P101", "pos": [248, 59]},
                        "IO12": {"pin": "P100", "pos": [267, 59]},
                        "IO13": {"pin": "P99", "pos": [286, 59]},
                        "IO14": {"pin": "P98", "pos": [305, 59]},
                        "IO15": {"pin": "P97", "pos": [324, 59]},
                        "IO16": {"pin": "P95", "pos": [343, 59]},
                        "IO1": {"pin": "P118", "pos": [115, 40]},
                        "IO3": {"pin": "P116", "pos": [134, 40]},
                        "IO5": {"pin": "P114", "pos": [153, 40]},
                        "IO7": {"pin": "P111", "pos": [172, 40]},
                    },
                },
                "P7": {
                    "pins": {
                        "IO38": {"pin": "P143", "pos": [345, 733]},
                        "IO40": {"pin": "P141", "pos": [326, 733]},
                        "IO42": {"pin": "P139", "pos": [307, 733]},
                        "IO44": {"pin": "P137", "pos": [288, 733]},
                        "IO46": {"pin": "P133", "pos": [269, 733]},
                        "IO47": {"pin": "P132", "pos": [250, 733]},
                        "IO48": {"pin": "P131", "pos": [231, 733]},
                        "IO49": {"pin": "P127", "pos": [212, 733]},
                        "IO50": {"pin": "P126", "pos": [193, 733]},
                        "IO51": {"pin": "P124", "pos": [174, 733]},
                        "IO52": {"pin": "P123", "pos": [155, 733]},
                        "IO53": {"pin": "P121", "pos": [136, 733]},
                        "IO54": {"pin": "P120", "pos": [117, 733]},
                        "IO39": {"pin": "P142", "pos": [345, 752]},
                        "IO41": {"pin": "P140", "pos": [326, 752]},
                        "IO43": {"pin": "P138", "pos": [307, 752]},
                        "IO45": {"pin": "P134", "pos": [288, 752]},
                    },
                },
                "P2": {
                    "pins": {
                        "IO19": {"pin": "P94", "pos": [464, 59]},
                        "IO21": {"pin": "P92", "pos": [483, 59]},
                        "IO23": {"pin": "P87", "pos": [502, 59]},
                        "IO25": {"pin": "P84", "pos": [521, 59]},
                        "IO27": {"pin": "P82", "pos": [540, 59]},
                        "IO28": {"pin": "P81", "pos": [559, 59]},
                        "IO29": {"pin": "P80", "pos": [578, 59]},
                        "IO30": {"pin": "P79", "pos": [597, 59]},
                        "IO31": {"pin": "P78", "pos": [616, 59]},
                        "IO32": {"pin": "P75", "pos": [635, 59]},
                        "IO33": {"pin": "P62", "pos": [654, 59]},
                        "IO34": {"pin": "P61", "pos": [673, 59]},
                        "IO35": {"pin": "P59", "pos": [692, 59]},
                        "IO20": {"pin": "P93", "pos": [464, 40]},
                        "IO22": {"pin": "P88", "pos": [483, 40]},
                        "IO24": {"pin": "P85", "pos": [502, 40]},
                        "IO26": {"pin": "P83", "pos": [521, 40]},
                    },
                },
            },
            "7i92": {
                "P2": {
                    "pins": {
                        "IO0": {"pin": "P119", "pos": [125, 110]},
                        "IO2": {"pin": "P117", "pos": [144, 110]},
                        "IO4": {"pin": "P115", "pos": [163, 110]},
                        "IO6": {"pin": "P112", "pos": [182, 110]},
                        "IO8": {"pin": "P105", "pos": [201, 110]},
                        "IO9": {"pin": "P104", "pos": [220, 110]},
                        "IO10": {"pin": "P102", "pos": [239, 110]},
                        "IO11": {"pin": "P101", "pos": [258, 110]},
                        "IO12": {"pin": "P100", "pos": [277, 110]},
                        "IO13": {"pin": "P99", "pos": [296, 110]},
                        "IO14": {"pin": "P98", "pos": [315, 110]},
                        "IO15": {"pin": "P97", "pos": [334, 110]},
                        "IO16": {"pin": "P95", "pos": [353, 110]},
                        "IO1": {"pin": "P118", "pos": [125, 93]},
                        "IO3": {"pin": "P116", "pos": [144, 93]},
                        "IO5": {"pin": "P114", "pos": [163, 93]},
                        "IO7": {"pin": "P111", "pos": [182, 93]},
                    },
                },
                "P1": {
                    "pins": {
                        "IO17": {"pin": "P119", "pos": [125, 270]},
                        "IO19": {"pin": "P117", "pos": [144, 270]},
                        "IO21": {"pin": "P115", "pos": [163, 270]},
                        "IO23": {"pin": "P112", "pos": [182, 270]},
                        "IO25": {"pin": "P105", "pos": [201, 270]},
                        "IO26": {"pin": "P104", "pos": [220, 270]},
                        "IO27": {"pin": "P102", "pos": [239, 270]},
                        "IO28": {"pin": "P101", "pos": [258, 270]},
                        "IO29": {"pin": "P100", "pos": [277, 270]},
                        "IO30": {"pin": "P99", "pos": [296, 270]},
                        "IO31": {"pin": "P98", "pos": [315, 270]},
                        "IO32": {"pin": "P97", "pos": [334, 270]},
                        "IO33": {"pin": "P95", "pos": [353, 270]},
                        "IO18": {"pin": "P118", "pos": [125, 253]},
                        "IO20": {"pin": "P116", "pos": [144, 253]},
                        "IO22": {"pin": "P114", "pos": [163, 253]},
                        "IO24": {"pin": "P111", "pos": [182, 253]},
                    },
                },
            },
        }

        cardtype = self.plugin_setup.get("cardtype", self.option_default("cardtype"))
        board = cardtype.split("_")[0]
        self.IMAGE = f"{board}.png"

        slot = None
        pin_n = 0
        pinfile = os.path.join(os.path.dirname(__file__), "mesapins", board, f"{cardtype}.pin")
        # print(pinfile)
        pindata = open(pinfile, "r").read()
        for line in pindata.split("\n"):
            if line.startswith("IO Connections for "):
                slot = line.split()[3].split("+")[0]
                pin_n = 0
                # print(f"------- {slot} -------")
            elif slot is not None and "IOPort" in line:
                pin_n += 1
                io = line.split()[1]
                pos = pinpos.get(board, {}).get(slot, {}).get("pins", {}).get(f"IO{io}", {}).get("pos")
                func = line.split()[3].replace("None", "GPIO")
                if func != "GPIO":
                    pinfunc = line.split()[5].split("/")[0]
                    channel = line.split()[4].replace("None", "GPIO")
                    direction = line.split()[6].lstrip("(").rstrip(")").replace("In", "input").replace("Out", "output")
                    ptype = f"MESA{func}{pinfunc}-{channel}"
                    halname = f"hm2_7c81.0.{func.lower()}.{int(channel):02d}.{pinfunc.lower()}"
                else:
                    pinfunc = ""
                    channel = ""
                    direction = "all"
                    ptype = "GPIO"
                    halname = f"hm2_7c81.0.gpio.{int(io):03d}"
                # print(slot, f"IO{io}", func, pinfunc, direction, pos)
                if pos:
                    self.PINDEFAULTS[f"{slot}:P{pin_n}"] = {
                        "pin": halname,
                        "comment": f"{func}({channel}) - {pinfunc}",
                        "pos": pos,
                        "direction": direction,
                        "edge": "source",
                        "type": ptype,
                    }

    def precheck(self, parent):
        pass

    def hal(self, parent):
        pass

    def loader(cls, instances):
        output = []
        output.append("loadrt hostmot2")

        for num, instance in enumerate(instances):
            cardtype = instance.plugin_setup.get("cardtype", instance.option_default("cardtype"))
            board = cardtype.split("_")[0]
            card_bitfile = cardtype.split("_")[1]
            component = "hm2_rpspi"
            prefix = f"hm2_{board}.0"
            # output.append(f'loadrt {component} config="firmware=hm2/{board}/{card_bitfile}.BIT num_encoders=3 num_pwmgens=3 num_stepgens=12"')
            output.append(f'loadrt {component} config="firmware=hm2/{board}/{card_bitfile}.BIT"')
            output.append(f"setp {prefix}.watchdog.timeout_ns 5000000")
            output.append(f"setp {prefix}.dpll.01.timer-us -50")
            output.append(f"setp {prefix}.stepgen.timer-number 1")
            output.append("")
            output.append(f"addf {prefix}.read servo-thread")
            output.append(f"addf {prefix}.write servo-thread")
        return "\n".join(output)
