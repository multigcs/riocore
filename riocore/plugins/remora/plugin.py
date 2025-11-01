import copy
import os
import json
from riocore.plugins import PluginBase

import riocore

riocore_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))


class Plugin(PluginBase):
    def setup(self):
        self.NAME = "remora"
        self.COMPONENT = "remora"
        self.INFO = "remora"
        self.DESCRIPTION = "remora"
        self.KEYWORDS = "stepgen pwm remora board pico w5500"
        self.TYPE = "base"
        self.IMAGE_SHOW = False
        self.PLUGIN_TYPE = "remora"
        self.URL = "https://github.com/scottalford75/Remora-RP2040-W5500"
        self.SHORTENER = {
            "remora": "rea",
        }
        self.OPTIONS = {
            "node_type": {
                "default": "board",
                "type": "select",
                "options": [
                    "board",
                    "stepper",
                    "pwm",
                ],
                "description": "board type",
            },
        }

        extra_options = {
            "board": {
                "board": {
                    "default": "W5500-EVB-Pico",
                    "type": "select",
                    "options": [
                        "W5500-EVB-Pico",
                    ],
                    "description": "board type",
                },
                "mac": {
                    "default": "00:08:DC:12:34:56",
                    "type": str,
                    "description": "MAC-Address",
                },
                "ip": {
                    "default": "192.168.0.177",
                    "type": str,
                    "description": "IP-Address",
                },
                "mask": {
                    "default": "255.255.255.0",
                    "type": str,
                    "description": "Network-Mask",
                },
                "gw": {
                    "default": "192.168.10.1",
                    "type": str,
                    "description": "Gateway IP-Address",
                },
                "port": {
                    "default": 8888,
                    "type": int,
                    "description": "UDP-Port",
                },
            },
            "stepper": {},
            "pwm": {
                "frequency": {
                    "default": 10000,
                    "type": int,
                    "min": 1907,
                    "max": 1000000,
                    "description": "max pwm value",
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
                    "description": "max pwm value",
                },
            },
        }
        node_type = self.plugin_setup.get("node_type", self.option_default("node_type"))
        self.OPTIONS.update(extra_options[node_type])
        self.SIGNALS = {}

        if node_type == "board":
            board = self.plugin_setup.get("board", self.option_default("board"))
            self.TYPE = "base"
            self.IMAGE_SHOW = True
            self.IMAGE = f"{board}.png"
            self.BUILDER = ["build", "install"]
            board_pins = {
                "W5500-EVB-Pico": {
                    # "IO:LED": {"pin": f"{self.instances_name}:gp25", "pos": [259, 15], "direction": "all", "edge": "source", "type": ["GPIO"]},
                    "IO:GP15": {"pin": f"{self.instances_name}:gp15", "pos": [259, 15], "direction": "all", "edge": "source", "type": ["GPIO", "REMORAStepGenStep", "REMORAStepGenDir"]},
                    "IO:GP14": {
                        "pin": f"{self.instances_name}:gp14",
                        "pos": [281, 15],
                        "direction": "all",
                        "edge": "source",
                        "type": ["GPIO", "REMORAStepGenStep", "REMORAStepGenDir", "REMORAPwmPwm"],
                    },
                    "IO:GP13": {
                        "pin": f"{self.instances_name}:gp13",
                        "pos": [325, 15],
                        "direction": "all",
                        "edge": "source",
                        "type": ["GPIO", "REMORAStepGenStep", "REMORAStepGenDir", "REMORAPwmPwm"],
                    },
                    "IO:GP12": {"pin": f"{self.instances_name}:gp12", "pos": [347, 15], "direction": "all", "edge": "source", "type": ["GPIO", "REMORAStepGenStep", "REMORAStepGenDir"]},
                    "IO:GP11": {"pin": f"{self.instances_name}:gp11", "pos": [369, 15], "direction": "all", "edge": "source", "type": ["GPIO", "REMORAStepGenStep", "REMORAStepGenDir"]},
                    "IO:GP10": {"pin": f"{self.instances_name}:gp10", "pos": [391, 15], "direction": "all", "edge": "source", "type": ["GPIO", "REMORAStepGenStep", "REMORAStepGenDir"]},
                    "IO:GP9": {"pin": f"{self.instances_name}:gp9", "pos": [435, 15], "direction": "all", "edge": "source", "type": ["GPIO", "REMORAStepGenStep", "REMORAStepGenDir"]},
                    "IO:GP8": {
                        "pin": f"{self.instances_name}:gp8",
                        "pos": [457, 15],
                        "direction": "all",
                        "edge": "source",
                        "type": ["GPIO", "REMORAStepGenStep", "REMORAStepGenDir", "REMORAEncoderA"],
                    },
                    "IO:GP7": {
                        "pin": f"{self.instances_name}:gp7",
                        "pos": [479, 15],
                        "direction": "all",
                        "edge": "source",
                        "type": ["GPIO", "REMORAStepGenStep", "REMORAStepGenDir", "REMORAEncoderB"],
                    },
                    "IO:GP6": {"pin": f"{self.instances_name}:gp6", "pos": [501, 15], "direction": "all", "edge": "source", "type": ["GPIO", "REMORAStepGenStep", "REMORAStepGenDir"]},
                    "IO:GP5": {"pin": f"{self.instances_name}:gp5", "pos": [545, 15], "direction": "all", "edge": "source", "type": ["GPIO", "REMORAStepGenStep", "REMORAStepGenDir"]},
                    "IO:GP4": {"pin": f"{self.instances_name}:gp4", "pos": [567, 15], "direction": "all", "edge": "source", "type": ["GPIO", "REMORAStepGenStep", "REMORAStepGenDir"]},
                    "IO:GP3": {"pin": f"{self.instances_name}:gp3", "pos": [589, 15], "direction": "all", "edge": "source", "type": ["GPIO", "REMORAStepGenStep", "REMORAStepGenDir"]},
                    "IO:GP2": {"pin": f"{self.instances_name}:gp2", "pos": [611, 15], "direction": "all", "edge": "source", "type": ["GPIO", "REMORAStepGenStep", "REMORAStepGenDir"]},
                    "IO:GP1": {"pin": f"{self.instances_name}:gp1", "pos": [655, 15], "direction": "all", "edge": "source", "type": ["GPIO", "REMORAStepGenStep", "REMORAStepGenDir"]},
                    "IO:GP0": {"pin": f"{self.instances_name}:gp0", "pos": [677, 15], "direction": "all", "edge": "source", "type": ["GPIO", "REMORAStepGenStep", "REMORAStepGenDir"]},
                    # W5500 - SPI pins
                    # "IO:GP16": {"pin": f"{self.instances_name}:gp16", "pos": [259, 166], "direction": "all", "edge": "source", "type": ["GPIO", "REMORAStepGenStep", "REMORAStepGenDir"]},
                    # "IO:GP17": {"pin": f"{self.instances_name}:gp17", "pos": [281, 166], "direction": "all", "edge": "source", "type": ["GPIO", "REMORAStepGenStep", "REMORAStepGenDir"]},
                    # "IO:GP18": {"pin": f"{self.instances_name}:gp18", "pos": [325, 166], "direction": "all", "edge": "source", "type": ["GPIO", "REMORAStepGenStep", "REMORAStepGenDir"]},
                    # "IO:GP19": {"pin": f"{self.instances_name}:gp19", "pos": [347, 166], "direction": "all", "edge": "source", "type": ["GPIO", "REMORAStepGenStep", "REMORAStepGenDir"]},
                    # "IO:GP20": {"pin": f"{self.instances_name}:gp20", "pos": [369, 166], "direction": "all", "edge": "source", "type": ["GPIO", "REMORAStepGenStep", "REMORAStepGenDir"]},
                    # "IO:GP21": {"pin": f"{self.instances_name}:gp21", "pos": [391, 166], "direction": "all", "edge": "source", "type": ["GPIO", "REMORAStepGenStep", "REMORAStepGenDir"]},
                    "IO:GP22": {"pin": f"{self.instances_name}:gp22", "pos": [435, 166], "direction": "all", "edge": "source", "type": ["GPIO", "REMORAStepGenStep", "REMORAStepGenDir"]},
                    "IO:GP26": {"pin": f"{self.instances_name}:gp26", "pos": [479, 166], "direction": "all", "edge": "source", "type": ["GPIO", "REMORAStepGenStep", "REMORAStepGenDir"]},
                    "IO:GP27": {"pin": f"{self.instances_name}:gp27", "pos": [501, 166], "direction": "all", "edge": "source", "type": ["GPIO", "REMORAStepGenStep", "REMORAStepGenDir"]},
                    "IO:GP28": {"pin": f"{self.instances_name}:gp28", "pos": [545, 166], "direction": "all", "edge": "source", "type": ["GPIO", "REMORAStepGenStep", "REMORAStepGenDir"]},
                }
            }
            self.PINDEFAULTS = board_pins[board]
            self.remora_num = 0
        elif node_type == "stepper":
            self.TYPE = "joint"
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
                "step": {"direction": "output", "edge": "target", "type": "REMORAStepGenStep"},
                "dir": {"direction": "output", "edge": "target", "type": "REMORAStepGenDir"},
            }
        elif node_type == "pwm":
            self.TYPE = "io"
            self.IMAGE_SHOW = True
            self.IMAGES = ["spindle500w", "laser", "led"]
            scale = self.plugin_setup.get("scale", self.option_default("scale"))
            min_limit = self.plugin_setup.get("min_limit", self.option_default("min_limit"))
            self.SIGNALS = {
                "duty": {
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
                "pwm": {"direction": "output", "edge": "target", "type": "REMORAPwmPwm"},
            }

    def update_prefixes(cls, parent, instances):
        for instance in instances:
            node_type = instance.plugin_setup.get("node_type", instance.option_default("node_type"))
            if node_type == "board":
                stepgen_num = 0
                for connected_pin in parent.get_all_plugin_pins(configured=True, prefix=instance.instances_name):
                    name = connected_pin["name"]
                    plugin_instance = connected_pin["instance"]
                    if name == "step":
                        plugin_instance.PREFIX = f"stepgen-remora.{instance.remora_num}.stepgen.{stepgen_num}"
                        stepgen_num += 1
                    elif name == "pwm":
                        plugin_instance.PREFIX = f"stepgen-remora.{instance.remora_num}.pwm"

    def update_pins(self, parent):
        node_type = self.plugin_setup.get("node_type", self.option_default("node_type"))
        if node_type == "board":
            self.input_pins = []
            self.input_pullups = []
            self.output_pins = []
            self.pwm_pins = []
            self.pwm_inverts = []
            self.stepgen_steps = []
            self.stepgen_dirs = []
            self.stepgen_dir_inverts = []
            for connected_pin in parent.get_all_plugin_pins(configured=True, prefix=self.instances_name):
                name = connected_pin["name"]
                psetup = connected_pin["setup"]
                pin = connected_pin["pin"]
                direction = connected_pin["direction"]
                inverted = connected_pin["inverted"]

                if name == "step":
                    self.stepgen_steps.append(pin)
                elif name == "dir":
                    self.stepgen_dirs.append(pin)
                    self.stepgen_dir_inverts.append("0")
                elif name == "pwm":
                    self.pwm_pins.append(pin)
                    self.pwm_inverts.append("0")

                elif direction == "output":
                    self.output_pins.append(pin)
                    psetup["pin"] = f"stepgen-remora.{self.remora_num}.output.{pin.lower()}"
                elif direction == "input":
                    self.input_pins.append(pin)
                    self.input_pullups.append("1")
                    if inverted:
                        psetup["pin"] = f"stepgen-remora.{self.remora_num}.input.{pin.lower()}-not"
                    else:
                        psetup["pin"] = f"stepgen-remora.{self.remora_num}.input.{pin.lower()}"

    def component_loader(cls, instances):
        output = []
        for instance in instances:
            node_type = instance.plugin_setup.get("node_type", instance.option_default("node_type"))
            if node_type == "board":
                output.append("# stepgen-remora")
                ip = instance.plugin_setup.get("ip", instance.option_default("ip"))
                port = instance.plugin_setup.get("port", instance.option_default("port"))
                output.append(f'loadrt stepgen-remora ip_address="{ip}:{port}"')
                output.append("")
                output.append(f"addf stepgen-remora.{instance.remora_num}.watchdog-process servo-thread")
                output.append(f"addf stepgen-remora.{instance.remora_num}.process-send servo-thread")
                output.append(f"addf stepgen-remora.{instance.remora_num}.process-recv servo-thread")
        return "\n".join(output)

    def hal(self, parent):
        node_type = self.plugin_setup.get("node_type", self.option_default("node_type"))
        if node_type == "pwm":
            frequency = self.plugin_setup.get("frequency", self.option_default("frequency"))
            scale = self.plugin_setup.get("scale", self.option_default("scale"))
            min_limit = self.plugin_setup.get("min_limit", self.option_default("min_limit"))
            parent.halg.setp_add(f"{self.PREFIX}.frequency", frequency)
            parent.halg.setp_add(f"{self.PREFIX}.max-scale", scale)
            parent.halg.setp_add(f"{self.PREFIX}.min-limit", min_limit)
        elif node_type == "stepper":
            if "joint_data" in self.plugin_setup:
                joint_data = self.plugin_setup["joint_data"]
                axis_name = joint_data["axis"]
                joint_n = joint_data["num"]
                pid_num = joint_n
                if self.JOINT_TYPE == "velocity":
                    cmd_halname = f"{self.PREFIX}.command"
                    feedback_halname = f"{self.PREFIX}.feedback"
                    enable_halname = f"{self.PREFIX}.enable"
                    scale_halname = f"{self.PREFIX}.step-scale"
                    parent.halg.joint_add(
                        parent, axis_name, joint_n, "velocity", cmd_halname, feedback_halname=feedback_halname, scale_halname=scale_halname, enable_halname=enable_halname, pid_num=pid_num
                    )
                else:
                    cmd_halname = f"{self.PREFIX}.command"
                    feedback_halname = f"{self.PREFIX}.command"
                    enable_halname = f"{self.PREFIX}.enable"
                    scale_halname = f"{self.PREFIX}.step-scale"
                    parent.halg.joint_add(parent, axis_name, joint_n, "position", cmd_halname, feedback_halname=feedback_halname, scale_halname=scale_halname, enable_halname=enable_halname)

    def builder(self, config, command):
        project = riocore.Project(copy.deepcopy(config))
        firmware_path = os.path.join(project.config["output_path"], "Firmware", self.instances_name)
        cmd = f"cd {firmware_path} && make {command}"
        return cmd

    def extra_files(cls, parent, instances):
        remora_cfg = {
            "Board": "",
            "Modules": [],
        }
        for instance in instances:
            node_type = instance.plugin_setup.get("node_type", instance.option_default("node_type"))
            if node_type == "board":
                board = instance.plugin_setup.get("board", instance.option_default("board"))
                remora_cfg["Board"] = board
                data_bit = 0
                for connected_pin in parent.get_all_plugin_pins(configured=True, prefix="stepgen-remora"):
                    pin = connected_pin["pin"]
                    direction = connected_pin["direction"]
                    pinstance = connected_pin["instance"]
                    inverted = connected_pin["inverted"]
                    remora_cfg["Modules"].append(
                        {
                            "Thread": "Servo",
                            "Type": "Digital Pin",
                            "Comment": pinstance.title,
                            "Pin": pin.split(".")[-1].upper(),
                            "Mode": direction.title(),
                            "Data Bit": data_bit,
                            "Invert": "True" if inverted else "False",
                        }
                    )
                    data_bit += 1
        for instance in instances:
            node_type = instance.plugin_setup.get("node_type", instance.option_default("node_type"))
            if node_type == "stepper":
                axis = instance.plugin_setup["joint_data"]["axis"]
                jnum = instance.plugin_setup["joint_data"]["num"]
                remora_cfg["Modules"].append(
                    {
                        "Thread": "Base",
                        "Type": "Stepgen",
                        "Comment": f"{axis} - Joint {jnum} step generator",
                        "Joint Number": jnum,
                        "Step Pin": instance.plugin_setup["pins"]["step"]["pin"].split(":")[-1].upper(),
                        "Direction Pin": instance.plugin_setup["pins"]["dir"]["pin"].split(":")[-1].upper(),
                    }
                )
            elif node_type == "pwm":
                pass

        target = os.path.join(parent.component_path, "remora-config.txt")
        open(target, "w").write(json.dumps(remora_cfg, indent=4))
