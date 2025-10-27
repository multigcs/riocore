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
            "num_pwms": {
                "default": 1,
                "type": int,
                "min": 0,
                "max": 10,
                "description": "number of pwm's",
            },
            "num_encoders": {
                "default": 0,
                "type": int,
                "min": 0,
                "max": 10,
                "description": "number of encoder's",
            },
            "num_stepgens": {
                "default": 3,
                "type": int,
                "min": 0,
                "max": 10,
                "description": "number of stepgen's",
            },
            "num_serials": {
                "default": 0,
                "type": int,
                "min": 0,
                "max": 10,
                "description": "number of serial's",
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

        num_pwms = self.plugin_setup.get("num_pwms", self.option_default("num_pwms"))
        num_encoders = self.plugin_setup.get("num_encoders", self.option_default("num_encoders"))
        num_stepgens = self.plugin_setup.get("num_stepgens", self.option_default("num_stepgens"))
        num_serials = self.plugin_setup.get("num_serial", self.option_default("num_serials"))

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

                # filter unused pwm/encoder
                if func == "QCount":
                    channel = line.split()[4].replace("None", "GPIO")
                    if int(channel) >= num_encoders:
                        func = "GPIO"
                elif func == "PWM":
                    channel = line.split()[4].replace("None", "GPIO")
                    if int(channel) >= num_pwms:
                        func = "GPIO"
                elif func == "StepGen":
                    channel = line.split()[4].replace("None", "GPIO")
                    if int(channel) >= num_stepgens:
                        func = "GPIO"
                elif func == "SSerial":
                    channel = line.split()[4].replace("None", "GPIO")
                    if int(channel) >= num_serials:
                        func = "GPIO"

                if func == "GPIO":
                    pinfunc = ""
                    channel = ""
                    direction = "all"
                    ptype = "GPIO"
                    halname = f"{self.instances_name}:gpio.{int(io):03d}"
                else:
                    pinfunc = line.split()[5].split("/")[0]
                    channel = line.split()[4].replace("None", "GPIO")
                    direction = line.split()[6].lstrip("(").rstrip(")").replace("In", "input").replace("Out", "output")
                    ptype = f"MESA{func}{pinfunc}-{channel}"
                    halname = f"{self.instances_name}:{func.lower()}.{int(channel):02d}.{pinfunc.lower()}"

                # print(slot, f"IO{io}", func, channel, pinfunc, direction, pos)
                if pos:
                    mapping_to_db25 = [0, 1, 14, 2, 15, 3, 16, 4, 17, 5, 6, 7, 8, 9, 10, 11, 12, 13]
                    mpin_n = mapping_to_db25[pin_n]
                    self.PINDEFAULTS[f"{slot}:P{mpin_n}"] = {
                        "pin": halname,
                        "comment": f"{func}({channel}) - {pinfunc}",
                        "pos": pos,
                        "direction": direction,
                        "edge": "source",
                        "type": ptype,
                    }

        cardtype = self.plugin_setup.get("cardtype", self.option_default("cardtype"))
        board = cardtype.split("_")[0]
        self.instance_num = 0
        self.hm2_prefix = f"hm2_{board}.{self.instance_num}"

    def precheck(self, parent):
        pass

    def hal(self, parent):
        for plugin_instance in parent.project.plugin_instances:
            if plugin_instance.PLUGIN_TYPE in {"gpio", "mesa"}:
                for name, psetup in plugin_instance.plugin_setup.get("pins", {}).items():
                    if "pin" not in psetup:
                        continue
                    pin = psetup["pin"]
                    if ":" not in pin:
                        continue
                    prefix = pin.split(":")[0]
                    if prefix != self.instances_name:
                        continue
                    pin = pin.split(":")[1]

                    direction = plugin_instance.PINDEFAULTS[name]["direction"]
                    invert = 0
                    for modifier in psetup.get("modifier", []):
                        if modifier["type"] == "invert":
                            invert = 1 - invert
                        else:
                            print(f"WARNING: modifier {modifier['type']} is not supported for gpio's")

                    if pin.endswith(".step") or pin.endswith(".dir"):
                        pin = pin.replace(".step", "").replace(".dir", "")
                        psetup["pin"] = f"{self.hm2_prefix}.{pin}.out"
                    elif direction == "output":
                        psetup["pin"] = f"{self.hm2_prefix}.{pin}.out"
                        parent.halg.setp_add(f"{self.hm2_prefix}.{pin}.is_output", 1)
                        if invert:
                            parent.halg.setp_add(f"{self.hm2_prefix}.{pin}.invert_output", 1)
                    elif direction == "input":
                        if invert:
                            psetup["pin"] = f"{self.hm2_prefix}.{pin}.in_not"
                        else:
                            psetup["pin"] = f"{self.hm2_prefix}.{pin}.in"

    def loader(cls, instances):
        output = []
        output.append("loadrt hostmot2")

        # mesaflash --device 7C81 --addr /dev/spidev0.0 --spi --fix-boot-block --write 7c81_5abobx3d.bit
        # is_opendrain
        # invert_output

        for num, instance in enumerate(instances):
            cardtype = instance.plugin_setup.get("cardtype", instance.option_default("cardtype"))
            num_pwms = instance.plugin_setup.get("num_pwm", instance.option_default("num_pwm"))
            num_encoders = instance.plugin_setup.get("num_encoders", instance.option_default("num_encoders"))
            num_stepgens = instance.plugin_setup.get("num_stepgens", instance.option_default("num_stepgens"))
            # num_serials = instance.plugin_setup.get("num_serial", instance.option_default("num_serial"))

            board = cardtype.split("_")[0]
            # card_bitfile = cardtype.split("_")[1]
            prefix = f"hm2_{board}.0"

            if cardtype.startswith("7c81"):
                component = "hm2_rpspi"
                output.append(f'loadrt {component} spi_probe=1 spiclk_rate=11250 config="num_encoders={num_encoders} num_pwmgens={num_pwms} num_stepgens={num_stepgens}" ')
            else:
                component = "hm2_eth"
                output.append(f'loadrt {component} board_ip="192.168.10.15" config="num_encoders={num_encoders} num_pwmgens={num_pwms} num_stepgens={num_stepgens}" ')

            output.append(f"setp {prefix}.watchdog.timeout_ns 5000000")
            output.append(f"setp {prefix}.dpll.01.timer-us -50")
            output.append(f"setp {prefix}.stepgen.timer-number 1")
            output.append("")
            output.append(f"addf {prefix}.read servo-thread")
            output.append(f"addf {prefix}.write servo-thread")
        return "\n".join(output)
