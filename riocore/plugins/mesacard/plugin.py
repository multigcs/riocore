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
                ],
                "description": "card configuration",
            },
        }
        self.SIGNALS = {}
        self.PINDEFAULTS = {}

        pinpos = {
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
        }

        cardtype = self.plugin_setup.get("cardtype", self.option_default("cardtype"))
        board = cardtype.split("_")[0]
        # print(f"/usr/src/MXM/riocore/mesact_firmware/{board}/{cardtype}.pin")

        slot = None
        pin_n = 0
        pindata = open(f"/usr/src/MXM/riocore/mesact_firmware/{board}/{cardtype}.pin", "r").read()
        for line in pindata.split("\n"):
            if line.startswith("IO Connections for "):
                slot = line.split()[3].split("+")[0]
                pin_n = 0
                # print("-------")
            elif slot is not None and "IOPort" in line:
                pin_n += 1
                io = line.split()[1]
                pos = pinpos.get(slot, {}).get("pins", {}).get(f"IO{io}", {}).get("pos")

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

                if pos:
                    # print(slot, f"IO{io}", func, pinfunc, direction, pos)
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
        output.append('loadrt hm2_rpspi config="firmware=hm2/7c81/5ABOBX3.BIT num_encoders=3 num_pwmgens=3 num_stepgens=12"')
        output.append("setp hm2_7c81.0.watchdog.timeout_ns 5000000")
        output.append("setp hm2_7c81.0.dpll.01.timer-us -50")
        output.append("setp hm2_7c81.0.stepgen.timer-number 1")
        output.append("")
        output.append("addf hm2_7c81.0.read servo-thread")
        output.append("addf hm2_7c81.0.write servo-thread")
        return "\n".join(output)
