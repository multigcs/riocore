import copy
import glob
import json
import os
import platform

import riocore

from riocore.plugins import PluginBase

from .generator.component import component
from .generator.gateware import gateware
from .generator.jslib import jslib
from .generator.mqttbridge import mqttbridge
from .generator.pylib import pylib
from .generator.rosbridge import rosbridge
from .generator.simulator import simulator

riocore_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))


class Plugin(PluginBase):
    def setup(self):
        self.NAME = "fpga"
        self.INFO = "fpga board"
        self.DESCRIPTION = "fpga"
        self.KEYWORDS = "fpga board"
        self.TYPE = "base"
        self.IMAGE_SHOW = False
        self.PROVIDES = ["fpga", "base"]
        self.BUILDER = ["clean", "build", "load", "all"]
        self.URL = ""
        self.frame = "full"
        board_list = []
        for jboard in glob.glob(os.path.join(os.path.dirname(__file__), "boards", "*.json")):
            board_list.append(os.path.basename(jboard).replace(".json", ""))

        self.OPTIONS = {
            "node_type": {
                "default": "",
                "type": "select",
                "options": sorted(board_list),
                "description": "board type",
                "reload": True,
            },
            "simulation": {
                "default": False,
                "type": bool,
                "description": "simulation mode",
            },
        }
        node_type = self.plugin_setup.get("node_type", self.option_default("node_type"))
        if node_type == "":
            return
        board_file = os.path.join(os.path.dirname(__file__), "boards", f"{node_type}.json")
        self.jdata = json.loads(open(board_file).read())
        self.PROVIDES += self.jdata.get("provides", [])

        if toolchains := self.jdata.get("toolchains"):
            if "gowin" in toolchains and platform.machine() != "x86_64":
                toolchains.remove("gowin")
                if self.jdata.get("toolchain") == "gowin":
                    self.jdata["toolchain"] = "icestorm"
            self.OPTIONS.update(
                {
                    "toolchain": {
                        "default": self.jdata.get("toolchain", toolchains[0]),
                        "type": "select",
                        "options": toolchains,
                        "description": "used toolchain",
                    }
                }
            )
        if self.jdata.get("types"):
            self.OPTIONS.update(
                {
                    "chip_type": {
                        "default": self.jdata.get("type"),
                        "type": "select",
                        "options": self.jdata["types"],
                        "description": "used chip-type",
                    }
                }
            )

        use_internal = "OFF"
        internal_osc = self.jdata["clock"].get("internal")
        if internal_osc:
            self.OPTIONS.update(
                {
                    "use_internal": {
                        "default": "OFF",
                        "type": "select",
                        "options": ["OFF", *internal_osc],
                        "description": f"use internal clock {internal_osc}",
                        "reload": True,
                    }
                }
            )
            use_internal = self.plugin_setup.get("use_internal", self.option_default("use_internal"))

        clock_pin = (self.jdata["clock"].get("pin"),)
        osc = self.jdata["clock"].get("osc")
        if use_internal == "OFF" and clock_pin != "internal" and osc:
            self.OPTIONS.update(
                {
                    "speed": {
                        "default": int(self.jdata["clock"].get("speed", 0)),
                        "type": int,
                        "min": 1000000,
                        "max": 500000000,
                        "unit": "Hz",
                        "description": f"FPGA clock speed (default: {self.jdata['clock'].get('speed', 0)})",
                    }
                }
            )

        self.OPTIONS.update(
            {
                "flashcmd": {
                    "default": "",
                    "type": str,
                    "description": "overwrite flash command for this instance",
                }
            }
        )

        self.IMAGE = f"boards/{node_type}.png"
        self.IMAGE_SHOW = True
        self.DESCRIPTION = self.jdata.get("comment", "")
        self.INFO = self.jdata.get("description", "")
        self.URL = self.jdata.get("url", "")
        self.KEYWORDS = f"{node_type} board fpga gateware"
        self.PINDEFAULTS = {}
        for slot in self.jdata["slots"]:
            slot_name = slot["name"]
            for pin_name, pin_data in slot["pins"].items():
                if isinstance(pin_data, str):
                    slot["pins"][pin_name] = {"pin": pin_data}
                self.PINDEFAULTS[f"{slot_name}:{pin_name}"] = {
                    "edge": "source",
                    "optional": True,
                    "pintype": "FPGA",
                    "type": ["FPGA"],
                    "pin": f"{self.instances_name}:{pin_data['pin']}",
                    "pos": pin_data.get("pos", (0, 0)),
                    "rotate": pin_data.get("rotate", 0.0),
                    "visible": pin_data.get("visible", True),
                    "direction": pin_data.get("direction", "all"),
                    "comment": pin_data.get("comment", "all"),
                    "special": pin_data.get("special", False),
                    "marker": pin_data.get("marker", False),
                }

        self.fpga_num = 0
        self.hal_prefix = ""

        toolchain = self.plugin_setup.get("toolchain", self.option_default("toolchain")) or self.jdata.get("toolchain")
        if use_internal != "OFF":
            speed = int(use_internal)
            self.jdata["clock"]["pin"] = "internal"
            self.jdata["clock"]["speed"] = speed
            if "osc" in self.jdata["clock"]:
                del self.jdata["clock"]["osc"]

        speed = self.plugin_setup.get("speed", self.option_default("speed") or int(self.jdata["clock"].get("speed")))
        self.jdata["toolchain"] = toolchain
        self.jdata["clock"]["speed"] = speed
        self.jdata["speed"] = speed
        self.jdata["osc_clock"] = int(self.jdata["clock"].get("osc_clock") or self.jdata["speed"])
        self.jdata["sysclk_pin"] = self.jdata["clock"].get("pin")
        self.master = self.instances_name

        self.SUB_PLUGINS = []
        for spn, sub_plugin in enumerate(self.jdata.get("plugins", [])):
            if "uid" not in sub_plugin:
                sub_plugin["uid"] = f"{self.instances_name}_{sub_plugin['type']}{spn}"
            else:
                sub_plugin["uid"] = f"{self.instances_name}_{sub_plugin['uid']}"
            self.SUB_PLUGINS.append(sub_plugin)

        simulation = self.plugin_setup.get("simulation", self.option_default("simulation"))
        if simulation:
            self.SIGNALS["modbus_sim"] = {
                "direction": "output",
                "bool": True,
                "description": "modbus simulation",
                "display": {"section": "status", "title": "Modbus-Simulation"},
            }
            self.SIGNALS["modbus_debug"] = {
                "direction": "output",
                "bool": True,
                "description": "modbus simulation debug output",
                "display": {"section": "status", "title": "Modbus-Debug"},
            }

            self.OPTIONS.update(
                {
                    "modbus_port": {
                        "default": "",
                        "type": str,
                        "description": "modbus simulator serial port",
                    }
                }
            )

    @classmethod
    def update_prefixes(cls, parent, instances):
        for instance in instances:
            for connected_pin in parent.get_all_plugin_pins(configured=True, prefix=instance.instances_name):
                instance.hal_prefix = instance.instances_name
                if connected_pin["instance"].TYPE == "interface":
                    instance.interface_instance = connected_pin["instance"]
                    instance.protocol = instance.interface_instance.HOST_INTERFACE
                    instance.frame = connected_pin["instance"].plugin_setup.get("frame", "full")
                plugin_instance = connected_pin["instance"]
                plugin_instance.PREFIX = f"{instance.hal_prefix}.{plugin_instance.instances_name}"
                plugin_instance.MASTER_PROVIDES = instance.PROVIDES
                plugin_instance.master = instance.instances_name
                plugin_instance.gmaster = instance.instances_name
                instance.fmaster = None

        # copy sub interface options from connected plugin (like baud)
        for instance in instances:
            for connected_pin in parent.get_all_plugin_pins(configured=True, prefix=instance.instances_name):
                plugin_instance = connected_pin["instance"]
                for sub_pin in parent.get_all_plugin_pins(configured=True, prefix=plugin_instance.instances_name):
                    if plugin_instance.TYPE in {"interface", "sub_interface"}:
                        for option in plugin_instance.SUB_OPTIONS:
                            value = sub_pin["instance"].plugin_setup.get(option, sub_pin["instance"].option_default(option))
                            if value is not None:
                                plugin_instance.SUB_OPTIONS[option] = value

        subs = {}
        for instance in instances:
            for connected_pin in parent.get_all_plugin_pins(configured=True, prefix=instance.instances_name):
                plugin_instance = connected_pin["instance"]
                if plugin_instance.TYPE != "sub_interface":
                    continue
                for sub_pin in parent.get_all_plugin_pins(configured=True, prefix=plugin_instance.instances_name):
                    if sub_pin["instance"].gmaster is None:
                        sub_pin["instance"].gmaster = instance.instances_name
                    plugin_instance.SUBBOARD = sub_pin["instance"].master
                    subs[plugin_instance.SUBBOARD] = instance.instances_name

        for instance in instances:
            for connected_pin in parent.get_all_plugin_pins(configured=True, prefix=instance.instances_name):
                instance.hal_prefix = instance.instances_name
                plugin_instance = connected_pin["instance"]
                if subs.get(instance.instances_name):
                    master = subs[instance.instances_name]
                    plugin_instance.PREFIX = f"{master}.{instance.hal_prefix}.{plugin_instance.instances_name}"
                    plugin_instance.gmaster = master  # gateware master
                    instance.fmaster = master  # fpga master (connected to the PC)

    def update_pins(self, parent):
        for connected_pin in parent.get_all_plugin_pins(configured=True, prefix=self.instances_name):
            psetup = connected_pin["setup"]
            pin = connected_pin["pin"]
            psetup["pin"] = pin

    def hal(self, parent):
        if self.fmaster:
            return
        parent.halg.net_add("iocontrol.0.user-request-enable", f"{self.hal_prefix}.sys-enable-request", "user-request-enable")
        parent.halg.net_add("iocontrol.0.user-enable-out", f"{self.hal_prefix}.sys-enable", "user-enable-out")
        parent.halg.net_add(f"&{self.hal_prefix}.sys-status", "iocontrol.0.emc-enable-in")
        parent.halg.net_add(f"{self.hal_prefix}.sys-error", "halui.estop.activate")

    def start_sh(self, parent):
        return f'# sudo halcompile --install "$DIRNAME/riocomp-{self.instances_name}.c"\n'

    @classmethod
    def component_loader(cls, instances):
        output = []

        comp_names = []
        for instance in instances:
            node_type = instance.plugin_setup.get("node_type", instance.option_default("node_type"))
            simulation = instance.plugin_setup.get("simulation", instance.option_default("simulation"))
            if instance.fmaster:
                # is sub fpga
                continue
            comp_names.append(f"riocomp-{instance.instances_name}")
            output.append(f"# fpga board(s) {node_type}")

        output.append(f"loadrt rio comp_names={','.join(comp_names)}")
        output.append("")

        for instance in instances:
            node_type = instance.plugin_setup.get("node_type", instance.option_default("node_type"))
            simulation = instance.plugin_setup.get("simulation", instance.option_default("simulation"))
            if instance.fmaster:
                # is sub fpga
                continue

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
            return None
        return f"cd {gateware_path} && make {command}"

    @classmethod
    def extra_files(cls, parent, instances):
        for instance in instances:
            gateware_path = os.path.join(parent.project.config["output_path"], "Gateware", instance.instances_name)
            firmware_path = os.path.join(parent.project.config["output_path"], "Firmware", instance.instances_name)
            parent.gateware_path = gateware_path
            instance.jdata["flashcmd"] = instance.plugin_setup.get("flashcmd", instance.jdata.get("flashcmd"))
            instance.jdata["name"] = instance.plugin_setup.get("node_type", instance.option_default("node_type"))
            instance.jdata["json_path"] = parent.project.config["json_path"]
            instance.jdata["riocore_path"] = riocore_path
            instance.jdata["output_path"] = gateware_path
            # overwrite flash command if exsist in json config
            if "flashcmd" in parent.project.config["jdata"]:
                instance.jdata["flashcmd"] = parent.project.config["jdata"]["flashcmd"]
            # overwrite flash command if exsist in plugin config
            if "flashcmd" in instance.plugin_setup:
                instance.jdata["flashcmd"] = instance.plugin_setup["flashcmd"]
            # overwrite chip type if exsist
            if "chip_type" in instance.plugin_setup:
                instance.jdata["type"] = instance.plugin_setup["chip_type"]
            instance.BUILDER_PATH = gateware_path

            # clean None pins
            for plugin_instance in parent.project.plugin_instances:
                for pin_config in plugin_instance.plugin_setup.get("pins", {}).values():
                    if "pin" in pin_config and not pin_config["pin"]:
                        del pin_config["pin"]

            parent.project.config["speed"] = instance.jdata["speed"]

            # gateware
            instance.gateware = gateware(parent, instance)
            if instance.jdata["toolchain"]:
                instance.gateware.generator()

            # linuxcnc-component
            if not instance.fmaster:
                component(parent.project, instance=instance)
                rosbridge(parent.project, instance=instance)
                mqttbridge(parent.project, instance=instance)
                pylib(parent.project, instance=instance)
                if instance.protocol == "UDP":
                    jslib(parent.project, instance=instance)
                    simulator(parent.project, instance=instance)
            elif not instance.jdata["toolchain"]:
                instance.jdata["output_path"] = firmware_path
                instance.firmware(parent, instances)

            chain = [instance.instances_name]
            if instance.master != instance.instances_name:
                chain.append(instance.instances_name)
            if instance.gmaster and instance.gmaster != instance.fmaster:
                chain.append(instance.gmaster)
            if instance.protocol:
                chain.append(instance.protocol)
            if instance.fmaster:
                chain.append(instance.fmaster)
            if not instance.fmaster:
                chain.append("Host")
            riocore.log(f"  chain: {' -> '.join(chain)}")
