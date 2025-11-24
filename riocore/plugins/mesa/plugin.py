import os
import shutil
import copy
import glob
import json
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
                    "esp32",
                ],
                "description": "instance type",
                "reload": True,
            },
        }
        node_type = self.plugin_setup.get("node_type", self.option_default("node_type"))
        self.SIGNALS = {}

        if node_type == "esp32":
            self.OPTIONS.update(
                {
                    "board": {
                        "default": "esp32dev",
                        "type": "select",
                        "options": ["esp32dev", "wemos_d1_mini32", "pico"],
                        "description": "board type",
                    },
                    "cardname": {
                        "default": "9r01",
                        "type": "select",
                        "options": ["9r01", "9r02", "9r03", "9r04"],
                        "description": "card name",
                    },
                    "upload_port": {
                        "default": "/dev/ttyUSB0",
                        "type": str,
                        "description": "upload-port",
                    },
                },
            )

            board = self.plugin_setup.get("board", self.option_default("board"))

            if board == "pico":
                self.PINDEFAULTS = {
                    "SSERIAL:RX": {
                        "pin": f"{self.instances_name}:RX",
                        "direction": "all",
                        "pos": (10, 23 + 1 * 23),
                        "edge": "target",
                        "type": ["MESASSerialTX"],
                    },
                    "SSERIAL:TX": {
                        "pin": f"{self.instances_name}:TX",
                        "direction": "all",
                        "pos": (10, 23 + 0 * 23),
                        "edge": "target",
                        "type": ["MESASSerialRX"],
                    },
                }
                for pin_num, pin in enumerate((-1, -1, -1, 2, 3, 4, 5, -1, 6, 7, 8, 9, -1, 10, 11, 12, 13, -1, 14, 15)):
                    if pin == -1:
                        continue
                    self.PINDEFAULTS[f"IO:{pin}"] = {
                        "pin": f"{self.instances_name}:{pin}",
                        "direction": "all",
                        "pos": (10, 23 + pin_num * 23),
                        "edge": "source",
                        "type": ["GPIO"],
                    }
                for pin_num, pin in enumerate((-1, -1, -1, -1, -1, -1, 28, -1, 27, 26, -1, 22, -1, 21, 20, 19, 18, -1, 17, 16)):
                    if pin == -1:
                        continue
                    self.PINDEFAULTS[f"IO:{pin}"] = {
                        "pin": f"{self.instances_name}:{pin}",
                        "direction": "all",
                        "pos": (177, 23 + pin_num * 23),
                        "edge": "source",
                        "type": ["GPIO"],
                    }

            elif board == "esp32dev":
                self.PINDEFAULTS = {
                    "SSERIAL:RX": {
                        "pin": f"{self.instances_name}:RX",
                        "direction": "all",
                        "pos": (235, 50 + 9 * 23),
                        "edge": "target",
                        "type": ["MESASSerialTX"],
                    },
                    "SSERIAL:TX": {
                        "pin": f"{self.instances_name}:TX",
                        "direction": "all",
                        "pos": (235, 50 + 8 * 23),
                        "edge": "target",
                        "type": ["MESASSerialRX"],
                    },
                }
                for pin_num, pin in enumerate((-1, 36, 39, 34, 35, 32, 33, 25, 26, 27, 14, 12, 13)):
                    if pin == -1:
                        continue
                    self.PINDEFAULTS[f"IO:{pin}"] = {
                        "pin": f"{self.instances_name}:{pin}",
                        "direction": "all",
                        "pos": (10, 50 + pin_num * 23),
                        "edge": "source",
                        "type": ["GPIO"],
                    }
                for pin_num, pin in enumerate((23, 22, -1, -1, 21, 19, 18, 5, -1, -1, 4, 2, 15)):
                    if pin == -1:
                        continue
                    self.PINDEFAULTS[f"IO:{pin}"] = {
                        "pin": f"{self.instances_name}:{pin}",
                        "direction": "all",
                        "pos": (235, 50 + pin_num * 23),
                        "edge": "source",
                        "type": ["GPIO"],
                    }

            else:
                self.PINDEFAULTS = {
                    "SSERIAL:RX": {
                        "pin": f"{self.instances_name}:RX",
                        "direction": "all",
                        "pos": (240, 69 + 5 * 23),
                        "edge": "target",
                        "type": ["MESASSerialTX"],
                    },
                    "SSERIAL:TX": {
                        "pin": f"{self.instances_name}:TX",
                        "direction": "all",
                        "pos": (240, 69 + 4 * 23),
                        "edge": "target",
                        "type": ["MESASSerialRX"],
                    },
                }
                for pin_num, pin in enumerate((-1, -1, 39, 35, 33, 34, 14, -1, 9)):
                    if pin == -1:
                        continue
                    self.PINDEFAULTS[f"IO:{pin}"] = {
                        "pin": f"{self.instances_name}:{pin}",
                        "direction": "all",
                        "pos": (12, 69 + pin_num * 23),
                        "edge": "source",
                        "type": ["GPIO"],
                    }
                for pin_num, pin in enumerate((-1, 36, 26, 18, 19, 23, 5, 13, 10)):
                    if pin == -1:
                        continue
                    self.PINDEFAULTS[f"IO:{pin}"] = {
                        "pin": f"{self.instances_name}:{pin}",
                        "direction": "all",
                        "pos": (36, 69 + pin_num * 23),
                        "edge": "source",
                        "type": ["GPIO"],
                    }
                for pin_num, pin in enumerate((-1, -1, 22, 21, -1, -1, -1, -1, 15)):
                    if pin == -1:
                        continue
                    self.PINDEFAULTS[f"IO:{pin}"] = {
                        "pin": f"{self.instances_name}:{pin}",
                        "direction": "all",
                        "pos": (240, 69 + pin_num * 23),
                        "edge": "source",
                        "type": ["GPIO"],
                    }
                for pin_num, pin in enumerate((-1, 27, 25, 32, 12, 4, 0, 2)):
                    if pin == -1:
                        continue
                    self.PINDEFAULTS[f"IO:{pin}"] = {
                        "pin": f"{self.instances_name}:{pin}",
                        "direction": "all",
                        "pos": (263, 69 + pin_num * 23),
                        "edge": "source",
                        "type": ["GPIO"],
                    }

            self.IMAGE_SHOW = True
            self.IMAGE = f"{board}.png"
            self.BUILDER = [
                "build",
                "load",
            ]

        elif node_type == "board":
            board_list = []
            for json_file in glob.glob(os.path.join(os.path.dirname(__file__), "*.json")):
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
                print("INFO: update config")
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

            posfile = os.path.join(os.path.dirname(__file__), f"{boardname}.json")
            if not os.path.exists(posfile):
                print(f"ERROR: boardfile not found: {posfile}")
                return
            board_pins = json.loads(open(posfile, "r").read())

            pinfile = os.path.join(os.path.dirname(__file__), "mesapins", boardname, f"{boardname}_{firmware}.pin")
            if not os.path.exists(pinfile):
                print(f"ERROR: boardfile not found: {pinfile}")
                return
            pindata = open(pinfile, "r").read()

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
            self.IMAGE = f"{boardname}.png"
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
                    # print(f"------- {slot} -------")
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
                        channel = f"{line.split()[4]}.{int(line.split()[5][-1]) - 1}"
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
                "pwm": {"direction": "output", "edge": "target", "type": ["MESAPwmPwm", "MESAPWMPWM"]},
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
        elif node_type == "esp32":
            project = riocore.Project(copy.deepcopy(config))
            firmware_path = os.path.join(project.config["output_path"], "Firmware", self.instances_name)
            cmd = f"cd {firmware_path} && make {command}"
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
                        plugin_instance.PREFIX = f"{instance.hm2_prefix}"
                        plugin_instance.SSERIAL_NUM = ".".join(rawpin.split(".")[-2:])
                    else:
                        plugin_instance.PREFIX = f"{instance.hm2_prefix}.{suffix}"
            elif node_type == "esp32":
                cardname = instance.plugin_setup.get("cardname", instance.option_default("cardname"))
                pwm_n = 0
                for connected_pin in parent.get_all_plugin_pins(configured=True, prefix=instance.instances_name):
                    rawpin = connected_pin["rawpin"]
                    plugin_instance = connected_pin["instance"]
                    plugin_instance.hm2_prefix = f"{instance.PREFIX}.{cardname}.{instance.SSERIAL_NUM}"
                    if connected_pin["name"] == "pwm":
                        plugin_instance.PREFIX = f"{instance.PREFIX}.{cardname}.{instance.SSERIAL_NUM}.pwm{pwm_n}"
                        del plugin_instance.SIGNALS["enable"]

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

        elif node_type == "esp32":
            self.pins_input = []
            self.pins_output = []
            self.pins_pwm = []
            input_pin_n = 0
            output_pin_n = 0
            pwm_pin_n = 0
            for connected_pin in parent.get_all_plugin_pins(configured=True, prefix=self.instances_name):
                psetup = connected_pin["setup"]
                pin = connected_pin["pin"]
                direction = connected_pin["direction"]
                inverted = connected_pin["inverted"]
                plugin_instance = connected_pin["instance"]
                if direction == "input":
                    self.pins_input.append(pin)
                    if inverted:
                        psetup["pin"] = f"{plugin_instance.hm2_prefix}.input-{input_pin_n:02d}-not"
                    else:
                        psetup["pin"] = f"{plugin_instance.hm2_prefix}.input-{input_pin_n:02d}"
                    input_pin_n += 1
                else:
                    if connected_pin["name"] == "pwm":
                        self.pins_pwm.append(pin)
                        psetup["pin"] = f"{plugin_instance.hm2_prefix}.pwm-{pwm_pin_n:02d}"
                        pwm_pin_n += 1
                    else:
                        self.pins_output.append(pin)
                        if inverted:
                            self.output_inverts.append(f"{plugin_instance.hm2_prefix}.output-{output_pin_n:02d}")
                        psetup["pin"] = f"{plugin_instance.hm2_prefix}.output-{output_pin_n:02d}"
                        output_pin_n += 1

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
        elif node_type == "esp32":
            for pin in self.output_inverts:
                parent.halg.setp_add(f"{pin}-invert", 1)
        elif node_type == "pwm":
            if self.PREFIX:
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

    def extra_files(cls, parent, instances):
        for instance in instances:
            node_type = instance.plugin_setup.get("node_type", instance.option_default("node_type"))
            if node_type == "esp32":
                board = instance.plugin_setup.get("board", instance.option_default("board"))
                cardname = instance.plugin_setup.get("cardname", instance.option_default("cardname"))
                upload_port = instance.plugin_setup.get("upload_port", instance.option_default("upload_port"))
                bits_out = len(instance.pins_output)
                bits_in = max(1, len(instance.pins_input))  # we need at least 1 bit
                int_size_in = 8
                int_size_out = 8
                for int_size in (8, 16, 32):
                    if bits_in <= int_size:
                        int_size_in = int_size
                        break
                for int_size in (8, 16, 32):
                    if bits_out <= int_size:
                        int_size_out = int_size
                        break

                byte_size_in = int_size_in // 8
                byte_size_out = int_size_out // 8

                input_pin_n = 0
                output_pin_n = 0
                for connected_pin in parent.get_all_plugin_pins(configured=True, prefix=instance.instances_name):
                    psetup = connected_pin["setup"]
                    pin = connected_pin["pin"]
                    direction = connected_pin["direction"]
                    inverted = connected_pin["inverted"]
                    plugin_instance = connected_pin["instance"]
                    if direction == "input":
                        if inverted:
                            psetup["pin"] = f"{plugin_instance.hm2_prefix}.input-{input_pin_n:02d}-not"
                        else:
                            psetup["pin"] = f"{plugin_instance.hm2_prefix}.input-{input_pin_n:02d}"
                        input_pin_n += 1
                    else:
                        psetup["pin"] = f"{plugin_instance.hm2_prefix}.output-{output_pin_n:02d}"
                        output_pin_n += 1
                    print("+##", connected_pin)

                # create firmware stuff
                firmware_path = os.path.join(parent.project.config["output_path"], "Firmware", instance.instances_name)
                os.makedirs(firmware_path, exist_ok=True)
                os.makedirs(os.path.join(firmware_path, "src"), exist_ok=True)
                os.makedirs(os.path.join(firmware_path, "lib"), exist_ok=True)
                print(f"  {instance.instances_name}: create firmware structure: {firmware_path}")

                output = []
                source = os.path.join(os.path.dirname(__file__), "sserial", "TEMPLATE.ino")
                for line in open(source, "r").read().split("\n"):
                    if line.strip() == "//defines":
                        output.append(f"#define BOARD \"{board}\"")
                        if board == "pico":
                            output.append("#define SSerial Serial1")
                        else:
                            output.append("#define SSerial Serial2")
                        output.append("")

                    elif line.strip() == "//LBP_Discovery_Data":
                        output.append("static const LBP_Discovery_Data DISCOVERY_DATA =")
                        output.append("{")
                        if bits_in:
                            output.append("  .RxSize = sizeof(ProcessDataOut)+1, // +1 for the fault status, remote transmits")
                        else:
                            output.append("  .RxSize = 1, // +1 for the fault status, remote transmits")
                        if bits_out or instance.pins_pwm:
                            output.append("  .TxSize = sizeof(ProcessDataIn), // remote receives")
                        else:
                            output.append("  .TxSize = 0, // remote receives")
                        output.append("  .ptoc   = PTOC_BASE_ADDRESS,")
                        output.append("  .gtoc   = GTOC_BASE_ADDRESS")
                        output.append("};")

                        output.append("")

                    elif line.strip() == "//ProcessDataOut":
                        output.append("static struct ProcessDataOut {")
                        output.append("    uint8_t fault;")
                        if bits_in:
                            output.append(f"    uint{int_size_in}_t input;")
                        output.append("} pdata_out = {0x00000000};")
                        output.append("")
                    elif line.strip() == "//ProcessDataIn":
                        if bits_out or instance.pins_pwm:
                            output.append("static struct ProcessDataIn {")
                            for pwm_num, pwm in enumerate(instance.pins_pwm):
                                output.append(f"    float pwm{pwm_num};")
                            if bits_out:
                                output.append(f"    uint{int_size_out}_t output;")
                            output.append("} pdata_in = {0x00000000};")
                            output.append("")
                    elif line.strip() == "//CARD_NAME":
                        output.append(f'static const char CARD_NAME[] = "{cardname}";')
                        output.append("")
                    elif line.strip() == "//PDD":
                        offset = 0
                        for pwm_num, pwm in enumerate(instance.pins_pwm):
                            output.append("    {")
                            output.append("        .pdd = {")
                            output.append("            .RecordType    = LBP_PDD_RECORD_TYPE_NORMAL,")
                            output.append("            .DataSize      = 32,")
                            output.append("            .DataType      = LBP_PDD_DATA_TYPE_FLOAT,")
                            output.append("            .DataDirection = LBP_PDD_DIRECTION_OUTPUT,")
                            output.append("            .ParamMin      = 0.0,")
                            output.append("            .ParamMax      = 0.0,")
                            output.append(f"            .ParamAddress  = PARAM_BASE_ADDRESS + {offset},")
                            output.append(f'            "None\\0Pwm{pwm_num}"')
                            output.append("        }")
                            output.append("    },")
                            offset += 4
                        if bits_out:
                            output.append("    {")
                            output.append("        .pdd = {")
                            output.append("            .RecordType    = LBP_PDD_RECORD_TYPE_NORMAL,")
                            output.append(f"            .DataSize      = {bits_out},")
                            output.append("            .DataType      = LBP_PDD_DATA_TYPE_BITS,")
                            output.append("            .DataDirection = LBP_PDD_DIRECTION_OUTPUT,")
                            output.append("            .ParamMin      = 0.0,")
                            output.append("            .ParamMax      = 0.0,")
                            output.append("            .ParamAddress  = PARAM_BASE_ADDRESS,")
                            output.append('            "None\\0Output"')
                            output.append("        }")
                            output.append("    },")
                            offset += byte_size_out
                        if bits_in:
                            output.append("    {")
                            output.append("        .pdd = {")
                            output.append("            .RecordType    = LBP_PDD_RECORD_TYPE_NORMAL,")
                            output.append(f"            .DataSize      = {bits_in},")
                            output.append("            .DataType      = LBP_PDD_DATA_TYPE_BITS,")
                            output.append("            .DataDirection = LBP_PDD_DIRECTION_INPUT,")
                            output.append("            .ParamMin      = 0.0,")
                            output.append("            .ParamMax      = 0.0,")
                            output.append(f"            .ParamAddress  = PARAM_BASE_ADDRESS + {offset},")
                            output.append('            "None\\0Input"')
                            output.append("        }")
                            output.append("    },")
                            offset += byte_size_in

                        output.append("")

                    elif line.strip() == "//PTOC":
                        output.append("static const uint16_t PTOC[] = {")
                        offset = 2
                        if bits_out:
                            output.append(f"    PDD_BASE_ADDRESS+{offset}*sizeof(LBP_PDD),")
                            offset += 1
                        if bits_in:
                            output.append(f"    PDD_BASE_ADDRESS+{offset}*sizeof(LBP_PDD),")
                            offset += 1
                        for pwm in instance.pins_pwm:
                            output.append(f"    PDD_BASE_ADDRESS+{offset}*sizeof(LBP_PDD),")
                            offset += 1
                        output.append("    0x0000")
                        output.append("};")
                        output.append("")
                    elif line.strip() == "//GTOC":
                        output.append("static const uint16_t GTOC[] = {")
                        output.append("    PDD_BASE_ADDRESS,")
                        offset = 1
                        output.append(f"    PDD_BASE_ADDRESS+{offset}*sizeof(LBP_PDD),")
                        offset += 1
                        if bits_out:
                            output.append(f"    PDD_BASE_ADDRESS+{offset}*sizeof(LBP_PDD),")
                            offset += 1
                        if bits_in:
                            output.append(f"    PDD_BASE_ADDRESS+{offset}*sizeof(LBP_PDD),")
                            offset += 1
                        for pwm in instance.pins_pwm:
                            output.append(f"    PDD_BASE_ADDRESS+{offset}*sizeof(LBP_PDD),")
                            offset += 1
                        output.append("    0x0000")
                        output.append("};")
                        output.append("")

                    elif line.strip() == "//setup":
                        for pin_num, pin in enumerate(instance.pins_output):
                            output.append(f"    pinMode({pin}, OUTPUT); // Output({pin_num:02d})")
                        for pin_num, pin in enumerate(instance.pins_input):
                            output.append(f"    pinMode({pin}, INPUT_PULLUP); // Input({pin_num:02d})")
                        for pin_num, pin in enumerate(instance.pins_pwm):
                            output.append(f"    pinMode({pin}, OUTPUT); // PWM({pin_num})")
                        output.append("")

                    elif line.strip() == "//pdata_in_next":
                        if bits_out or instance.pins_pwm:
                            output.append("            uint8_t pdata_in_next[sizeof(pdata_in)];")
                            output.append("            if (cmd.value == LBP_COMMAND_RPC_SMARTSERIAL_PROCESS_DATA) {")
                            output.append("                for (size_t i = 0; i < sizeof(pdata_in); i++) {")
                            output.append("                    while (!SSerial.available()) {yield();}")
                            output.append("                    const uint8_t c = SSerial.read();")
                            output.append("                    crc = LBP_CalcNextCRC(c, crc);")
                            output.append("                    pdata_in_next[i] = c;")
                            output.append("                }")
                            output.append("            }")
                            output.append("")

                    elif line.strip() == "//pdata_out.input":
                        if bits_in:
                            output.append("                    pdata_out.input = 0;")
                            for pin_num, pin in enumerate(instance.pins_input):
                                output.append(f"                    if (digitalRead({pin})) {{")
                                output.append(f"                        pdata_out.input |= (1<<{pin_num});")
                                output.append("                    }")
                        output.append("")

                    elif line.strip() == "//pdata_in.output":
                        if bits_out or instance.pins_pwm:
                            output.append("                    memcpy(&pdata_in, pdata_in_next, sizeof(pdata_in));")
                            for pin_num, pin in enumerate(instance.pins_output):
                                output.append(f"                    digitalWrite({pin}, (pdata_in.output & (1<<{pin_num})) ? HIGH : LOW);")

                            for pwm_num, pwm in enumerate(instance.pins_pwm):
                                output.append(f"                    // pdata_in.pwm{pwm_num};")

                            output.append("")

                    else:
                        output.append(line)

                target = os.path.join(firmware_path, "src", "main.ino")
                open(target, "w").write("\n".join(output))

                output = [""]
                output.append(f"[env:{board}]")
                output.append("framework = arduino")
                output.append(f"board = {board}")
                if board == "pico":
                    output.append("platform = raspberrypi")
                else:
                    output.append("platform = espressif32")
                    output.append("#upload_speed = 115200")
                    output.append("upload_speed = 500000")
                    output.append("monitor_speed = 115200")
                    output.append(f"upload_port = {upload_port}")
                output.append("")
                output.append("")
                target = os.path.join(firmware_path, "platformio.ini")
                open(target, "w").write("\n".join(output))

                output = [""]
                output.append("build:")
                output.append("	pio run")
                output.append("")
                output.append("load:")
                output.append("	pio run --target=upload")
                output.append("")
                target = os.path.join(firmware_path, "Makefile")
                open(target, "w").write("\n".join(output))

                for filename in ("LBP.cpp", "LBP.h"):
                    source = os.path.join(os.path.dirname(__file__), "sserial", filename)
                    target = os.path.join(firmware_path, "src", filename)
                    shutil.copy(source, target)
