import glob
import json
import os

import riocore
from riocore.plugins import PluginBase

riocore_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))


class Plugin(PluginBase):
    def setup(self):
        self.NAME = "mesa"
        self.COMPONENT = "mesa"
        self.INFO = "support for mesa-cards with hm2 firmware"
        self.DESCRIPTION = """
## flashing 7i92
mesaflash --device 7i92 --addr 10.10.10.10  --write /mnt/data2/src/riocore/MI^C/mesact_firmware/7i92/7i92_G540x2D.bit
        """
        self.KEYWORDS = "stepgen pwm mesa board hm2"
        self.TYPE = "base"
        self.IMAGE_SHOW = False
        self.PLUGIN_TYPE = "mesa"
        self.URL = ""
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
                "reload": True,
            },
        }
        node_type = self.plugin_setup.get("node_type", self.option_default("node_type"))
        self.SIGNALS = {}

        if node_type == "board":
            board_list = []
            for json_file in glob.glob(os.path.join(os.path.dirname(__file__), "boards", "*.json")):
                board = json_file.split("/")[-1][:-5]
                board_list.append(board)
            self.OPTIONS.update(
                {
                    "boardname": {
                        "default": board_list[0],
                        "type": "select",
                        "options": board_list,
                        "description": "card configuration",
                        "reload": True,
                    },
                }
            )

            board_old = self.plugin_setup.get("board")
            if board_old:
                riocore.log("INFO: update config")
                self.plugin_setup["boardname"] = board_old.split("_")[0]
                self.plugin_setup["firmware"] = board_old.split("_")[1]
                del self.plugin_setup["board"]

            boardname = self.plugin_setup.get("boardname", self.option_default("boardname"))
            self.instance_num = 0
            self.hm2_prefix = f"hm2_{boardname}.{self.instance_num}"

            fiirmware_list = []
            for pin_file in glob.glob(os.path.join(os.path.dirname(__file__), "mesapins", boardname, "*.pin")):
                fiirmware_list.append(pin_file.split("/")[-1][:-4].split("_", 1)[1])
            if not fiirmware_list:
                fiirmware_list = [""]
            self.OPTIONS.update(
                {
                    "firmware": {
                        "default": fiirmware_list[0],
                        "type": "select",
                        "options": fiirmware_list,
                        "description": "firmware",
                        "reload": True,
                    },
                }
            )
            firmware = self.plugin_setup.get("firmware", self.option_default("firmware"))

            posfile = os.path.join(os.path.dirname(__file__), "boards", f"{boardname}.json")
            if not os.path.exists(posfile):
                riocore.log(f"ERROR: boardfile not found: {posfile}")
                return
            board_pins = json.loads(open(posfile).read())

            pinfile = os.path.join(os.path.dirname(__file__), "mesapins", boardname, f"{boardname}_{firmware}.pin")
            if not os.path.exists(pinfile):
                riocore.log(f"ERROR: boardfile not found: {pinfile}")
                return
            pindata = open(pinfile).read()

            max_pwms = 0
            max_encoders = 0
            max_stepgens = 0
            max_serials = 0
            for line in pindata.split("\n"):
                if " of QCount in configuration" in line:
                    max_encoders = int(line.split()[2])
                elif " of StepGen in configuration" in line:
                    max_stepgens = int(line.split()[2])
                elif " of PWM in configuration" in line:
                    max_pwms = int(line.split()[2])
                elif " of SSerial in configuration" in line:
                    max_serials = int(line.split()[2])
            # MuxedQCount, MuxedQCountSel, SSR, SSI, PktUARTRXm PktUARTTX, PWMGen, Transformer, InMux, OutM, InM

            self.OPTIONS.update(
                {
                    "num_pwms": {
                        "default": 1,
                        "type": int,
                        "min": 0,
                        "max": max_pwms,
                        "description": "number of pwm's",
                    },
                    "num_encoders": {
                        "default": 0,
                        "type": int,
                        "min": 0,
                        "max": max_encoders,
                        "description": "number of encoder's",
                    },
                    "num_stepgens": {
                        "default": 3,
                        "type": int,
                        "min": 0,
                        "max": max_stepgens,
                        "description": "number of stepgen's",
                    },
                    "num_serials": {
                        "default": 0,
                        "type": int,
                        "min": 0,
                        "max": max_serials,
                        "description": "number of serial's",
                    },
                }
            )

            if boardname in {"7c80", "7c81"}:
                self.OPTIONS.update(
                    {
                        "spiclk_rate": {
                            "default": 21250,
                            "type": int,
                            "min": 10000,
                            "max": 1000000,
                            "description": "spiclk_rate",
                        },
                    }
                )
                self.BUILDER = [
                    f"readhmid: {board} (/dev/spidev0.0)",
                    f"flash: {board} (/dev/spidev0.0)",
                ]
            else:
                self.OPTIONS.update(
                    {
                        "ip_address": {
                            "default": "10.10.10.10",
                            "type": str,
                            "description": "ip address",
                        },
                    }
                )
                ip_address = self.plugin_setup.get("ip_address", self.option_default("ip_address"))
                self.BUILDER = [f"readhmid: {board} ({ip_address})", f"flash: {board} ({ip_address})"]

            self.TYPE = "base"
            self.IMAGE_SHOW = True
            self.IMAGE = f"boards/{boardname}.png"
            self.PINDEFAULTS = {}

            num_pwms = self.plugin_setup.get("num_pwms", self.option_default("num_pwms"))
            num_encoders = self.plugin_setup.get("num_encoders", self.option_default("num_encoders"))
            num_stepgens = self.plugin_setup.get("num_stepgens", self.option_default("num_stepgens"))
            num_serials = self.plugin_setup.get("num_serials", self.option_default("num_serials"))

            pin_n = 0
            slot = None
            for line in pindata.split("\n"):
                if line.startswith("IO Connections for "):
                    slot = line.split()[3].split("+")[0]
                    pin_n = 0
                    # riocore.log(f"------- {slot} -------")
                elif slot is not None and "IOPort" in line:
                    pin_n += 1
                    io = line.split()[1]

                    pos = board_pins["pins"].get(f"{slot}:IO{io}", {}).get("pos")
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
                    elif func.lower() == "sserial":
                        pinfunc = line.split()[5][:-5]
                        if line.split()[5][-3:-1] == "En":
                            pinfunc = "TxEnable"
                        channel = f"{line.split()[4]}.{int(line.split()[5][-1]) - 1}"
                        channel = f"{line.split()[4]}.{int(line.split()[5][-1])}"
                        direction = "all"
                        ptype = f"MESA{func}{pinfunc}-{channel}"
                        halname = f"{self.instances_name}:SSERIAL.{channel}"
                    else:
                        pinfunc = line.split()[5].split("/")[0]
                        func_halname = func.lower().replace("qcount", "encoder").replace("pwm", "pwmgen")
                        channel = line.split()[4].replace("None", "GPIO")
                        direction = line.split()[6].lstrip("(").rstrip(")").replace("In", "input").replace("Out", "output")
                        ptype = f"MESA{func}{pinfunc}-{channel}"
                        halname = f"{self.instances_name}:{func_halname}.{int(channel):02d}.{pinfunc.lower()}"

                    # riocore.log(slot, f"IO{io}", func, channel, pinfunc, direction, pos)
                    if pos:
                        mapping_to_db25 = [0, 1, 14, 2, 15, 3, 16, 4, 17, 5, 6, 7, 8, 9, 10, 11, 12, 13, "SS1", "SS2"]
                        mpin_n = mapping_to_db25[pin_n]
                        self.PINDEFAULTS[f"{slot}:P{mpin_n}"] = {
                            "pin": halname,
                            "comment": f"{func}({channel}) - {pinfunc}",
                            "pos": pos,
                            "direction": direction,
                            "edge": "source",
                            "type": ptype,
                        }

        elif node_type == "stepper":
            self.TYPE = "joint"
            self.JOINT_DEFAULTS = {
                "MESA_DIRSETUP": 2000,
                "MESA_DIRHOLD": 2000,
                "MESA_STEPLEN": 2000,
                "MESA_STEPSPACE": 2000,
                "MESA_STEPGEN_MAXVEL": 100,
                "MESA_STEPGEN_MAXACCEL": 1000,
            }
            self.JOINT_OPTIONS = list(self.JOINT_DEFAULTS)
            mode = self.plugin_setup.get("mode", self.option_default("mode"))
            if mode:
                self.JOINT_TYPE = "velocity"
            else:
                self.JOINT_TYPE = "position"
            self.IMAGE_SHOW = True
            self.IMAGES = ["stepper", "servo42", "stepstick"]
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
            self.OPTIONS.update(
                {
                    "scale": {
                        "default": 80,
                        "type": int,
                        "min": 1,
                        "max": 1000000,
                        "description": "encoder scale",
                    },
                }
            )

            self.TYPE = "io"
            self.IMAGE_SHOW = True
            self.IMAGE_SHOW = False
            self.IMAGES = ["generic", "encoder"]
            scale = self.plugin_setup.get("scale", self.option_default("scale"))
            self.SIGNALS = {
                "rawcounts": {
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
                "a": {"direction": "input", "edge": "target", "type": "MESAQCountQuad-A"},
                "b": {"direction": "input", "edge": "target", "type": "MESAQCountQuad-B"},
                "z": {"direction": "input", "edge": "target", "type": "MESAQCountQuad-IDX", "optional": True},
            }

        elif node_type == "pwm":
            self.OPTIONS.update(
                {
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
                }
            )

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
                "pwm": {"direction": "output", "edge": "target", "type": ["MESAPwmPwm", "MESAPWMPWM", "GPIO"]},
            }

    def builder(self, config, command):
        node_type = self.plugin_setup.get("node_type", self.option_default("node_type"))
        if node_type == "board":
            boardname = self.plugin_setup.get("boardname", self.option_default("boardname"))
            firmware = self.plugin_setup.get("firmware", self.option_default("firmware"))
            bitfile = os.path.join(os.path.dirname(__file__), "mesapins", boardname, f"{boardname}_{firmware}.bit")
            if boardname in {"7c80", "7c81"}:
                addr = "/dev/spidev0.0 --spi"
            else:
                addr = self.plugin_setup.get("ip_address", self.option_default("ip_address"))
            if command.startswith("flash:"):
                cmd = f"sudo mesaflash --device {boardname} --addr {addr} --write {bitfile}"
            else:
                cmd = f"sudo mesaflash --device {boardname} --addr {addr} --readhmid"
            return cmd

    def update_prefixes(cls, parent, instances):
        for instance in instances:
            node_type = instance.plugin_setup.get("node_type", instance.option_default("node_type"))
            if node_type == "board":
                for connected_pin in parent.get_all_plugin_pins(configured=True, prefix=instance.instances_name):
                    rawpin = connected_pin["rawpin"]
                    plugin_instance = connected_pin["instance"]
                    suffix = ".".join(rawpin.split(":")[1].split(".")[:-1])
                    if suffix.startswith("SSERIAL."):
                        plugin_instance.PREFIX = instance.hm2_prefix
                        plugin_instance.SSERIAL_NUM = ".".join(rawpin.split(".")[-2:])
                    else:
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
                # riocore.log(rawpin, pin, plugin_instance, suffix)
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
                boardname = instance.plugin_setup.get("boardname", instance.option_default("boardname"))
                num_pwms = instance.plugin_setup.get("num_pwms", instance.option_default("num_pwms"))
                num_encoders = instance.plugin_setup.get("num_encoders", instance.option_default("num_encoders"))
                num_stepgens = instance.plugin_setup.get("num_stepgens", instance.option_default("num_stepgens"))
                # num_serials = instance.plugin_setup.get("num_serials", instance.option_default("num_serials"))
                output.append("# mesa")
                if boardname in {"7c80", "7c81"}:
                    spiclk_rate = instance.plugin_setup.get("spiclk_rate", instance.option_default("spiclk_rate"))
                    component = "hm2_spix"
                    output.append("loadrt hostmot2")
                    output.append(f'loadrt {component} spi_probe=1 spiclk_rate={spiclk_rate} config="num_encoders={num_encoders} num_pwmgens={num_pwms} num_stepgens={num_stepgens}"')
                else:
                    ip_address = instance.plugin_setup.get("ip_address", instance.option_default("ip_address"))
                    output.append("loadrt hostmot2")
                    output.append(f'loadrt hm2_eth board_ip="{ip_address}" config="num_encoders={num_encoders} num_pwmgens={num_pwms} num_stepgens={num_stepgens}"')
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
            if self.PREFIX and ".pwm" in self.PREFIX:
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
                parent.halg.joint_add(parent, axis_name, joint_n, "velocity", cmd_halname, feedback_halname=feedback_halname, scale_halname=scale_halname, enable_halname=enable_halname, pid_num=pid_num)
                parent.halg.setp_add(f"{self.PREFIX}.control-type", "1")
                parent.halg.setp_add(f"{self.PREFIX}.step_type", "0")
