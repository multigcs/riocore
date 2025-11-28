import copy
import glob
import json
import os

import riocore
from riocore.plugins import PluginBase

from .generator.gateware import gateware
from .generator.component import component
from .generator.rosbridge import rosbridge
from .generator.mqttbridge import mqttbridge
from .generator.simulator import simulator
from .generator.jslib import jslib

riocore_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))


class Plugin(PluginBase):
    def setup(self):
        self.NAME = "fpga"
        self.COMPONENT = "fpga"
        self.INFO = "fpga board"
        self.DESCRIPTION = "fpga"
        self.KEYWORDS = "fpga board"
        self.TYPE = "base"
        self.IMAGE_SHOW = False
        self.PLUGIN_TYPE = "fpga"
        self.BUILDER = ["clean", "build", "load"]
        self.URL = ""
        board_list = []
        for jboard in glob.glob(os.path.join(os.path.dirname(__file__), "boards", "*.json")):
            board_list.append(os.path.basename(jboard).replace(".json", ""))
        self.OPTIONS = {
            "node_type": {
                "default": board_list[0],
                "type": "select",
                "options": board_list,
                "description": "board type",
                "reload": True,
            },
            "protocol": {
                "default": "SPI",
                "type": "select",
                "options": ["SPI", "UDP", "UART", "FTDI", "CH341", "SHM"],
                "description": "communication protocol",
            },
            "simulation": {
                "default": False,
                "type": bool,
                "description": "simulation mode",
            },
        }
        node_type = self.plugin_setup.get("node_type", self.option_default("node_type"))
        board_file = os.path.join(os.path.dirname(__file__), "boards", f"{node_type}.json")
        self.jdata = json.loads(open(board_file).read())
        if self.jdata.get("toolchains"):
            self.OPTIONS.update(
                {
                    "toolchain": {
                        "default": self.jdata.get("toolchain"),
                        "type": "select",
                        "options": self.jdata["toolchains"],
                    }
                }
            )

        self.OPTIONS.update(
            {
                "speed": {
                    "default": int(self.jdata["clock"].get("speed")),
                    "type": int,
                    "min": 1000000,
                    "max": 500000000,
                }
            }
        )

        self.IMAGE = f"boards/{node_type}.png"
        self.IMAGE_SHOW = True
        self.DESCRIPTION = self.jdata.get("comment", "")
        self.INFO = self.jdata.get("description", "")
        self.KEYWORDS = f"{node_type} board fpga gateware"
        self.PINDEFAULTS = {}
        for slot in self.jdata["slots"]:
            slot_name = slot["name"]
            for pin_name, pin_data in slot["pins"].items():
                if isinstance(pin_data, str):
                    pin_data = {"pin": pin_data}
                self.PINDEFAULTS[f"{slot_name}:{pin_name}"] = {
                    "edge": "source",
                    "optional": True,
                    "pintype": "FPGA",
                    "type": ["FPGA"],
                    "pin": f"{self.instances_name}:{pin_data['pin']}",
                    "pos": pin_data.get("pos", (0, 0)),
                    "visible": pin_data.get("visible", True),
                    "direction": pin_data.get("direction", "all"),
                }

        self.fpga_num = 0
        self.hal_prefix = ""

        toolchain = self.plugin_setup.get("toolchain", self.option_default("toolchain")) or self.jdata.get("toolchain")
        speed = self.plugin_setup.get("speed", self.option_default("speed"))
        protocol = self.plugin_setup.get("protocol", self.option_default("protocol"))
        self.jdata["protocol"] = protocol
        self.jdata["toolchain"] = toolchain
        self.jdata["speed"] = speed
        self.jdata["osc_clock"] = int(self.jdata["clock"].get("osc_clock", self.jdata["speed"]))
        self.jdata["sysclk_pin"] = self.jdata["clock"].get("pin")
        self.master = self.instances_name

        self.SUB_PLUGINS = []
        for spn, sub_plugin in enumerate(self.jdata.get("plugins", [])):
            if "uid" not in sub_plugin:
                sub_plugin["uid"] = f"{self.instances_name}_{sub_plugin['type']}{spn}"
            else:
                sub_plugin["uid"] = f"{self.instances_name}_{sub_plugin['uid']}"
            self.SUB_PLUGINS.append(sub_plugin)

    def update_prefixes(cls, parent, instances):
        subs = {}
        for instance in instances:
            for connected_pin in parent.get_all_plugin_pins(configured=True, prefix=instance.instances_name):
                if connected_pin["instance"].NAME == "uartsub":
                    subboard = connected_pin["instance"].plugin_setup.get("subboard")
                    if subboard:
                        subs[subboard] = instance.instances_name

        for instance in instances:
            for connected_pin in parent.get_all_plugin_pins(configured=True, prefix=instance.instances_name):
                instance.hal_prefix = instance.instances_name
                plugin_instance = connected_pin["instance"]
                plugin_instance.PREFIX = f"{instance.hal_prefix}.{plugin_instance.instances_name}"
                plugin_instance.master = instance.instances_name
                plugin_instance.gmaster = instance.instances_name

                if subs.get(instance.instances_name):
                    master = subs[instance.instances_name]
                    plugin_instance.PREFIX = f"{master}.{instance.hal_prefix}.{plugin_instance.instances_name}"
                    plugin_instance.gmaster = master

    def update_pins(self, parent):
        for connected_pin in parent.get_all_plugin_pins(configured=True, prefix=self.instances_name):
            psetup = connected_pin["setup"]
            pin = connected_pin["pin"]
            psetup["pin"] = pin

    def hal(self, parent):
        parent.halg.net_add("iocontrol.0.user-enable-out", f"{self.hal_prefix}.sys-enable", "user-enable-out")
        parent.halg.net_add("iocontrol.0.user-request-enable", f"{self.hal_prefix}.sys-enable-request", "user-request-enable")
        parent.halg.net_add(f"&{self.hal_prefix}.sys-status", "iocontrol.0.emc-enable-in")
        parent.halg.net_add("halui.machine.is-on", f"{self.hal_prefix}.machine-on")

    def start_sh(self, parent):
        return f'sudo halcompile --install "$DIRNAME/riocomp-{self.instances_name}.c"\n'

    def component_loader(cls, instances):
        output = []
        for instance in instances:
            node_type = instance.plugin_setup.get("node_type", instance.option_default("node_type"))
            simulation = instance.plugin_setup.get("simulation", instance.option_default("simulation"))
            protocol = instance.plugin_setup.get("protocol", instance.option_default("protocol"))

            if protocol == "UART":
                # is sub fpga
                continue

            output.append(f"# fpga board {node_type}")
            output.append(f"loadrt riocomp-{instance.instances_name}")
            output.append("")
            output.append("# if you need to test rio without hardware, set it to 1")
            if simulation:
                output.append(f"setp {instance.hal_prefix}.sys-simulation 1")
            else:
                output.append(f"setp {instance.hal_prefix}.sys-simulation 0")
            output.append("")
            output.append(f"addf {instance.hal_prefix}.readwrite servo-thread")
        return "\n".join(output)

    def builder(self, config, command):
        if not isinstance(config, dict):
            project = config
        else:
            project = riocore.Project(copy.deepcopy(config))
        gateware_path = os.path.join(project.config["output_path"], "Gateware", self.instances_name)
        if not os.path.exists(gateware_path):
            riocore.log(f"ERROR: path not exist, please run generator first: {gateware_path}")
            return
        cmd = f"cd {gateware_path} && make {command}"
        return cmd

    def extra_files(cls, parent, instances):
        for instance in instances:
            gateware_path = os.path.join(parent.project.config["output_path"], "Gateware", instance.instances_name)
            instance.jdata["name"] = instance.plugin_setup.get("node_type", instance.option_default("node_type"))
            instance.jdata["json_path"] = parent.project.config["json_path"]
            instance.jdata["riocore_path"] = riocore_path
            instance.jdata["output_path"] = gateware_path
            instance.BUILDER_PATH = gateware_path

            # clean None pins
            for plugin_instance in parent.project.plugin_instances:
                if plugin_instance.PLUGIN_TYPE != "gateware":
                    continue
                for pin_config in plugin_instance.plugin_setup.get("pins", {}).values():
                    if "pin" in pin_config and not pin_config["pin"]:
                        del pin_config["pin"]

            parent.project.config["speed"] = instance.jdata["speed"]

            # gateware
            instance.gateware = gateware(parent, instance)
            instance.gateware.generator()

            # linuxcnc-component
            protocol = parent.project.config["protocol"] = instance.jdata["protocol"]
            if protocol != "UART":
                component(parent.project, instance=instance)
                rosbridge(parent.project, instance=instance)
                mqttbridge(parent.project, instance=instance)
                simulator(parent.project, instance=instance)
                jslib(parent.project, instance=instance)
