import glob
import importlib
import os

import riocore

from riocore.plugins import PluginBase

riocore_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))


class Plugin(PluginBase):
    def setup(self):
        self.NAME = "i2c_device"
        self.INFO = "i2c device"
        self.DESCRIPTION = "i2c device"
        self.KEYWORDS = "i2c"
        self.TYPE = "base"
        self.URL = ""
        self.IMAGE = ""
        self.IMAGE_SHOW = False
        self.SIGNALS = {}
        self.PINDEFAULTS = {}
        self.OPTIONS = {}
        self.NEEDS = ["i2c"]
        self.TYPE = "base"
        board_list = []
        for jboard in sorted(glob.glob(os.path.join(os.path.dirname(__file__), "boards", "*.py"))):
            board_list.append(os.path.basename(jboard).replace(".py", ""))

        self.OPTIONS.update(
            {
                "node_type": {
                    "default": "",
                    "type": "select",
                    "options": board_list,
                    "description": "device type",
                    "reload": True,
                },
            }
        )
        self.commands = {}
        self.command_ids = 0
        board = self.plugin_setup.get("node_type", self.option_default("node_type"))
        board_file = os.path.join(os.path.dirname(__file__), "boards", f"{board}.py")
        if os.path.exists(board_file):
            self.IMAGE = f"boards/{board}.png"
            self.IMAGE_SHOW = True
            board_lib = importlib.import_module(f".{board}", "riocore.plugins.i2c_device.boards")
            if hasattr(board_lib, "i2c_device"):
                board_instance = board_lib.i2c_device(self)
                board_instance.instances_name = self.instances_name
                board_instance.master = self.master
                self.PINDEFAULTS = board_instance.PINDEFAULTS
                self.INTERFACE = board_instance.INTERFACE
                self.SIGNALS = board_instance.SIGNALS
                self.INITS = board_instance.INITS
                self.STEPS = board_instance.STEPS
                self.options = board_instance.options
                if hasattr(board_instance, "convert_c"):
                    self.convert_c = board_instance.convert_c
                if hasattr(board_instance, "update_prefixes"):
                    self.update_prefixes = board_instance.update_prefixes
                if hasattr(board_instance, "update_pins"):
                    self.update_pins = board_instance.update_pins
                for signal_name, signal_data in self.SIGNALS.items():
                    if "interface" not in signal_data:
                        signal_data["interface"] = signal_name
                self.OPTIONS.update(
                    {
                        "address": {
                            "default": board_instance.options["addresses"][0],
                            "type": "select",
                            "options": board_instance.options["addresses"],
                            "description": "device address",
                        },
                        "speed": {
                            "type": int,
                            "description": "bus speed",
                            "min": 1000,
                            "max": 1000000,
                            "default": 100000,
                            "unit": "Hz",
                        },
                    }
                )
                if "config" in board_instance.options:
                    self.OPTIONS.update(board_instance.options["config"])
                if "info" in board_instance.options:
                    self.INFO = board_instance.options["info"]
                if "description" in board_instance.options:
                    self.DESCRIPTION = board_instance.options["description"]
        elif board != "":
            riocore.log(f"ERROR: modbus: boardfile not found: {board_file}")

    def gateware_instances(self):
        return None
