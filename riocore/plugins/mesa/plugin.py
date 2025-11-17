import os
from riocore.plugins import PluginBase

riocore_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))


class Plugin(PluginBase):
    def setup(self):
        self.NAME = "mesa"
        self.COMPONENT = "mesa"
        self.INFO = "mesa"
        self.DESCRIPTION = "mesa"
        self.KEYWORDS = "stepgen pwm mesa board hm2"
        self.TYPE = "base"
        self.IMAGE_SHOW = False
        self.PLUGIN_TYPE = "mesa"
        self.URL = "https://github.com/atrex66/stepper-mesa"
        self.OPTIONS = {
            "node_type": {
                "default": "board",
                "type": "select",
                "options": [
                    "board",
                    "stepper",
                    "pwm",
                    "encoder",
                ],
                "description": "instance type",
            },
        }

        extra_options = {
            "board": {
                "board": {
                    "default": "7c81_5abobx3d",
                    "type": "select",
                    "options": [
                        "7c81_5abobx2d",
                        "7c81_5abobx3d",
                        "7i92_5ABOBx2D",
                    ],
                    "description": "card configuration",
                },
                "spiclk_rate": {
                    "default": 21250,
                    "type": int,
                    "min": 10000,
                    "max": 1000000,
                    "description": "spiclk_rate",
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
            },
            "stepper": {},
            "encoder": {
                "scale": {
                    "default": 80,
                    "type": int,
                    "min": 1,
                    "max": 1000000,
                    "description": "encoder scale",
                },
            },
            "pwm": {
                "frequency": {
                    "default": 10000,
                    "type": int,
                    "min": 1907,
                    "max": 1000000,
                    "description": "pwm frequency",
                },
                "scale": {
                    "default": 100,
                    "type": int,
                    "min": 1,
                    "max": 100000,
                    "description": "max pwm value",
                },
                "min_limit": {
                    "default": 0,
                    "type": int,
                    "min": 0,
                    "max": 100000,
                    "description": "min pwm value",
                },
            },
        }
        node_type = self.plugin_setup.get("node_type", self.option_default("node_type"))
        self.OPTIONS.update(extra_options[node_type])
        self.SIGNALS = {}

        if node_type == "board":
            board = self.plugin_setup.get("board", self.option_default("board"))
            board_type = board.split("_")[0]
            self.TYPE = "base"
            self.IMAGE_SHOW = True
            self.IMAGE = f"{board_type}.png"
            board_pins = {
                "7c81": {
                    "P1:IO0": {"pos": [115, 59]},
                    "P1:IO2": {"pos": [134, 59]},
                    "P1:IO4": {"pos": [153, 59]},
                    "P1:IO6": {"pos": [172, 59]},
                    "P1:IO8": {"pos": [191, 59]},
                    "P1:IO9": {"pos": [210, 59]},
                    "P1:IO10": {"pos": [229, 59]},
                    "P1:IO11": {"pos": [248, 59]},
                    "P1:IO12": {"pos": [267, 59]},
                    "P1:IO13": {"pos": [286, 59]},
                    "P1:IO14": {"pos": [305, 59]},
                    "P1:IO15": {"pos": [324, 59]},
                    "P1:IO16": {"pos": [343, 59]},
                    "P1:IO1": {"pos": [115, 40]},
                    "P1:IO3": {"pos": [134, 40]},
                    "P1:IO5": {"pos": [153, 40]},
                    "P1:IO7": {"pos": [172, 40]},
                    "P7:IO38": {"pos": [345, 733]},
                    "P7:IO40": {"pos": [326, 733]},
                    "P7:IO42": {"pos": [307, 733]},
                    "P7:IO44": {"pos": [288, 733]},
                    "P7:IO46": {"pos": [269, 733]},
                    "P7:IO47": {"pos": [250, 733]},
                    "P7:IO48": {"pos": [231, 733]},
                    "P7:IO49": {"pos": [212, 733]},
                    "P7:IO50": {"pos": [193, 733]},
                    "P7:IO51": {"pos": [174, 733]},
                    "P7:IO52": {"pos": [155, 733]},
                    "P7:IO53": {"pos": [136, 733]},
                    "P7:IO54": {"pos": [117, 733]},
                    "P7:IO39": {"pos": [345, 752]},
                    "P7:IO41": {"pos": [326, 752]},
                    "P7:IO43": {"pos": [307, 752]},
                    "P7:IO45": {"pos": [288, 752]},
                    "P2:IO19": {"pos": [464, 59]},
                    "P2:IO21": {"pos": [483, 59]},
                    "P2:IO23": {"pos": [502, 59]},
                    "P2:IO25": {"pos": [521, 59]},
                    "P2:IO27": {"pos": [540, 59]},
                    "P2:IO28": {"pos": [559, 59]},
                    "P2:IO29": {"pos": [578, 59]},
                    "P2:IO30": {"pos": [597, 59]},
                    "P2:IO31": {"pos": [616, 59]},
                    "P2:IO32": {"pos": [635, 59]},
                    "P2:IO33": {"pos": [654, 59]},
                    "P2:IO34": {"pos": [673, 59]},
                    "P2:IO35": {"pos": [692, 59]},
                    "P2:IO20": {"pos": [464, 40]},
                    "P2:IO22": {"pos": [483, 40]},
                    "P2:IO24": {"pos": [502, 40]},
                    "P2:IO26": {"pos": [521, 40]},
                },
                "7i92": {
                    "P2:IO0": {"pin": "P119", "pos": [125, 110]},
                    "P2:IO2": {"pin": "P117", "pos": [144, 110]},
                    "P2:IO4": {"pin": "P115", "pos": [163, 110]},
                    "P2:IO6": {"pin": "P112", "pos": [182, 110]},
                    "P2:IO8": {"pin": "P105", "pos": [201, 110]},
                    "P2:IO9": {"pin": "P104", "pos": [220, 110]},
                    "P2:IO10": {"pin": "P102", "pos": [239, 110]},
                    "P2:IO11": {"pin": "P101", "pos": [258, 110]},
                    "P2:IO12": {"pin": "P100", "pos": [277, 110]},
                    "P2:IO13": {"pin": "P99", "pos": [296, 110]},
                    "P2:IO14": {"pin": "P98", "pos": [315, 110]},
                    "P2:IO15": {"pin": "P97", "pos": [334, 110]},
                    "P2:IO16": {"pin": "P95", "pos": [353, 110]},
                    "P2:IO1": {"pin": "P118", "pos": [125, 93]},
                    "P2:IO3": {"pin": "P116", "pos": [144, 93]},
                    "P2:IO5": {"pin": "P114", "pos": [163, 93]},
                    "P2:IO7": {"pin": "P111", "pos": [182, 93]},
                    "P1:IO17": {"pin": "P119", "pos": [125, 270]},
                    "P1:IO19": {"pin": "P117", "pos": [144, 270]},
                    "P1:IO21": {"pin": "P115", "pos": [163, 270]},
                    "P1:IO23": {"pin": "P112", "pos": [182, 270]},
                    "P1:IO25": {"pin": "P105", "pos": [201, 270]},
                    "P1:IO26": {"pin": "P104", "pos": [220, 270]},
                    "P1:IO27": {"pin": "P102", "pos": [239, 270]},
                    "P1:IO28": {"pin": "P101", "pos": [258, 270]},
                    "P1:IO29": {"pin": "P100", "pos": [277, 270]},
                    "P1:IO30": {"pin": "P99", "pos": [296, 270]},
                    "P1:IO31": {"pin": "P98", "pos": [315, 270]},
                    "P1:IO32": {"pin": "P97", "pos": [334, 270]},
                    "P1:IO33": {"pin": "P95", "pos": [353, 270]},
                    "P1:IO18": {"pin": "P118", "pos": [125, 253]},
                    "P1:IO20": {"pin": "P116", "pos": [144, 253]},
                    "P1:IO22": {"pin": "P114", "pos": [163, 253]},
                    "P1:IO24": {"pin": "P111", "pos": [182, 253]},
                },
            }
            self.PINDEFAULTS = {}

            num_pwms = self.plugin_setup.get("num_pwms", self.option_default("num_pwms"))
            num_encoders = self.plugin_setup.get("num_encoders", self.option_default("num_encoders"))
            num_stepgens = self.plugin_setup.get("num_stepgens", self.option_default("num_stepgens"))
            num_serials = self.plugin_setup.get("num_serials", self.option_default("num_serials"))
            pinfile = os.path.join(os.path.dirname(__file__), "mesapins", board_type, f"{board}.pin")

            # print(pinfile)
            pin_n = 0
            slot = None
            pindata = open(pinfile, "r").read()
            for line in pindata.split("\n"):
                if line.startswith("IO Connections for "):
                    slot = line.split()[3].split("+")[0]
                    pin_n = 0
                    # print(f"------- {slot} -------")
                elif slot is not None and "IOPort" in line:
                    pin_n += 1
                    io = line.split()[1]

                    pos = board_pins[board_type].get(f"{slot}:IO{io}", {}).get("pos")
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
                        func_halname = func.replace("PWM", "pwmgen").lower()
                        channel = line.split()[4].replace("None", "GPIO")
                        direction = line.split()[6].lstrip("(").rstrip(")").replace("In", "input").replace("Out", "output")
                        ptype = f"MESA{func}{pinfunc}-{channel}"
                        halname = f"{self.instances_name}:{func_halname}.{int(channel):02d}.{pinfunc.lower()}"

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

            # print(self.PINDEFAULTS)
            self.instance_num = 0
            self.hm2_prefix = f"hm2_{board_type}.{self.instance_num}"

        elif node_type == "stepper":
            self.TYPE = "joint"
            self.JOINT_OPTIONS = ["MESA_DIRSETUP", "MESA_DIRHOLD", "MESA_STEPLEN", "MESA_STEPSPACE", "MESA_STEPGEN_MAXVEL", "MESA_STEPGEN_MAXACCEL"]
            mode = self.plugin_setup.get("mode", self.option_default("mode"))
            if mode:
                self.JOINT_TYPE = "velocity"
            else:
                self.JOINT_TYPE = "position"
            self.IMAGE_SHOW = True
            self.IMAGES = ["stepper", "servo42"]
            self.SIGNALS = {
                "velocity": {
                    "direction": "output",
                    "absolute": False,
                    "description": "set position",
                },
                "position": {
                    "direction": "input",
                    "unit": "steps",
                    "absolute": False,
                    "description": "position feedback",
                },
                "position-scale": {
                    "direction": "output",
                    "absolute": False,
                    "description": "steps / unit",
                },
            }
            self.PINDEFAULTS = {
                "step": {"direction": "output", "edge": "target", "type": "MESAStepGenStep"},
                "dir": {"direction": "output", "edge": "target", "type": "MESAStepGenDir"},
            }
        elif node_type == "encoder":
            self.TYPE = "io"
            self.IMAGE_SHOW = True
            self.IMAGE_SHOW = False
            self.IMAGES = ["generic", "encoder"]
            scale = self.plugin_setup.get("scale", self.option_default("scale"))
            self.SIGNALS = {
                "raw-count": {
                    "direction": "input",
                    "s32": True,
                },
                "position": {
                    "direction": "input",
                },
                "velocity": {
                    "direction": "input",
                },
                "count-latched": {
                    "direction": "input",
                    "s32": True,
                },
                "position-latched": {
                    "direction": "input",
                },
            }
            self.PINDEFAULTS = {
                "a": {"direction": "output", "edge": "target", "type": "MESAEncoderA"},
                "b": {"direction": "output", "edge": "target", "type": "MESAEncoderB"},
                "z": {"direction": "output", "edge": "target", "type": "MESAEncoderZ", "optional": True},
            }

        elif node_type == "pwm":
            self.TYPE = "io"
            self.IMAGE_SHOW = True
            self.IMAGES = ["spindle500w", "laser", "led"]
            scale = self.plugin_setup.get("scale", self.option_default("scale"))
            min_limit = self.plugin_setup.get("min_limit", self.option_default("min_limit"))
            self.SIGNALS = {
                "value": {
                    "direction": "output",
                    "min": min_limit,
                    "max": scale,
                },
                "enable": {
                    "direction": "output",
                    "bool": True,
                },
            }
            self.PINDEFAULTS = {
                "pwm": {"direction": "output", "edge": "target", "type": "MESAPwmPwm"},
            }

    def update_prefixes(cls, parent, instances):
        for instance in instances:
            node_type = instance.plugin_setup.get("node_type", instance.option_default("node_type"))
            if node_type == "board":
                for connected_pin in parent.get_all_plugin_pins(configured=True, prefix=instance.instances_name):
                    rawpin = connected_pin["rawpin"]
                    plugin_instance = connected_pin["instance"]
                    suffix = ".".join(rawpin.split(":")[1].split(".")[:-1])
                    plugin_instance.PREFIX = f"{instance.hm2_prefix}.{suffix}"

    def update_pins(self, parent):
        self.outputs = []
        self.output_inverts = []
        node_type = self.plugin_setup.get("node_type", self.option_default("node_type"))
        if node_type == "board":
            for connected_pin in parent.get_all_plugin_pins(configured=True, prefix=self.instances_name):
                psetup = connected_pin["setup"]
                pin = connected_pin["pin"]
                direction = connected_pin["direction"]
                inverted = connected_pin["inverted"]
                # print(rawpin, pin, plugin_instance, suffix)
                if pin.startswith("gpio."):
                    if direction == "input":
                        if inverted:
                            psetup["pin"] = f"{self.hm2_prefix}.{pin.lower()}.in_not"
                        else:
                            psetup["pin"] = f"{self.hm2_prefix}.{pin.lower()}.in"
                    else:
                        psetup["pin"] = f"{self.hm2_prefix}.{pin.lower()}.out"
                        self.outputs.append(f"{self.hm2_prefix}.{pin.lower()}")
                        if inverted:
                            self.output_inverts.append(f"{self.hm2_prefix}.{pin.lower()}")
                else:
                    del psetup["pin"]

    def component_loader(cls, instances):
        output = []
        for instance in instances:
            node_type = instance.plugin_setup.get("node_type", instance.option_default("node_type"))
            if node_type == "board":
                board = instance.plugin_setup.get("board", instance.option_default("board"))
                board_type = board.split("_")[0]

                num_pwms = instance.plugin_setup.get("num_pwms", instance.option_default("num_pwms"))
                num_encoders = instance.plugin_setup.get("num_encoders", instance.option_default("num_encoders"))
                num_stepgens = instance.plugin_setup.get("num_stepgens", instance.option_default("num_stepgens"))
                spiclk_rate = instance.plugin_setup.get("spiclk_rate", instance.option_default("spiclk_rate"))

                output.append("# mesa")

                if board_type == "7i92":
                    ip_address = "192.168.1.121"
                    output.append("loadrt hostmot2")
                    output.append(f'loadrt hm2_eth board_ip="{ip_address}" config="num_encoders={num_encoders} num_pwmgens={num_pwms} num_stepgens={num_stepgens}"')
                    output.append(f"setp {instance.hm2_prefix}.watchdog.timeout_ns 50000000")
                    output.append(f"setp {instance.hm2_prefix}.dpll.01.timer-us -50")
                    output.append(f"setp {instance.hm2_prefix}.stepgen.timer-number 1")
                    output.append("")
                    output.append(f"addf {instance.hm2_prefix}.read servo-thread")
                    output.append(f"addf {instance.hm2_prefix}.write servo-thread")

                else:
                    component = "hm2_spix"
                    output.append("loadrt hostmot2")
                    output.append(f'loadrt {component} spi_probe=1 spiclk_rate={spiclk_rate} config="num_encoders={num_encoders} num_pwmgens={num_pwms} num_stepgens={num_stepgens}"')
                    output.append(f"setp {instance.hm2_prefix}.led.CR01 1")
                    output.append(f"setp {instance.hm2_prefix}.led.CR02 1")
                    output.append(f"setp {instance.hm2_prefix}.led.CR03 1")
                    output.append(f"setp {instance.hm2_prefix}.led.CR04 1")
                    output.append(f"setp {instance.hm2_prefix}.watchdog.timeout_ns 50000000")
                    output.append(f"setp {instance.hm2_prefix}.dpll.01.timer-us -50")
                    output.append(f"setp {instance.hm2_prefix}.stepgen.timer-number 1")
                    output.append("")
                    output.append(f"addf {instance.hm2_prefix}.read servo-thread")
                    output.append(f"addf {instance.hm2_prefix}.write servo-thread")

        return "\n".join(output)

    def hal(self, parent):
        node_type = self.plugin_setup.get("node_type", self.option_default("node_type"))
        if node_type == "board":
            for pin in self.outputs:
                parent.halg.setp_add(f"{pin}.is_output", 1)
            for pin in self.output_inverts:
                parent.halg.setp_add(f"{pin}.invert_output", 1)
        elif node_type == "pwm":
            scale = self.plugin_setup.get("scale", self.option_default("scale"))
            parent.halg.setp_add(f"{self.PREFIX}.scale", scale)

        elif node_type == "encoder":
            scale = self.plugin_setup.get("scale", self.option_default("scale"))
            parent.halg.setp_add(f"{self.PREFIX}.scale", scale)
        elif node_type == "stepper":
            if "joint_data" in self.plugin_setup:
                joint_data = self.plugin_setup["joint_data"]
                axis_name = joint_data["axis"]
                joint_n = joint_data["num"]
                pid_num = joint_n

                for key in ("dirsetup", "dirhold", "steplen", "stepspace", "stepgen_maxvel", "stepgen_maxaccel"):
                    value = f"MESA_{key.upper()}"
                    parent.halg.setp_add(f"{self.PREFIX}.{key.replace('stepgen_', '')}", f"[JOINT_{joint_n}]{value}")

                cmd_halname = f"{self.PREFIX}.velocity-cmd"
                feedback_halname = f"{self.PREFIX}.position-fb"
                enable_halname = f"{self.PREFIX}.enable"
                scale_halname = f"{self.PREFIX}.position-scale"
                parent.halg.joint_add(
                    parent, axis_name, joint_n, "velocity", cmd_halname, feedback_halname=feedback_halname, scale_halname=scale_halname, enable_halname=enable_halname, pid_num=pid_num
                )
                parent.halg.setp_add(f"{self.PREFIX}.control-type", "1")
                parent.halg.setp_add(f"{self.PREFIX}.step_type", "0")
