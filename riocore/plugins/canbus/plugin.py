from riocore.plugins import PluginBase
from struct import pack, unpack

class Plugin(PluginBase):
    def setup(self):
        self.NAME = "canbus"
        self.INFO = "odrive canbus test"
        self.DESCRIPTION = ""
        self.KEYWORDS = "canbus odrive"
        self.ORIGIN = ""
        # self.LIMITATIONS = {}
        self.TYPE = "joint"

        self.VERILOGS = ["canbus.v"]

        self.OPTIONS = {
            "baud": {
                "default": 250000,
                "type": int,
                "min": 300,
                "max": 10000000,
                "unit": "bit/s",
                "description": "serial baud rate",
            },
        }
        self.PINDEFAULTS = {
            "tx": {
                "direction": "output",
            },
            "rx": {
                "direction": "input",
            },
        }
        self.INTERFACE = {
            "position": {
                "size": 32,
                "is_float": True,
                "direction": "input",
                "description": "",
            },
            "velocity": {
                "size": 32,
                "is_float": True,
                "direction": "output",
                "description": "",
            },
            "enable": {
                "size": 1,
                "direction": "output",
                "on_error": False,
            },
        }
        self.SIGNALS = {
            "position": {
                "direction": "input",
                "format": "0.2f",
                "unit": "",
            },
            "velocity": {
                "direction": "output",
                "min": -10,
                "max": 10,
                "format": "0.2f",
                "unit": "",
            },
            "enable": {
                "direction": "output",
                "bool": True,
            },
        }

    def gateware_instances(self):
        instances = self.gateware_instances_base()
        instance = instances[self.instances_name]
        instance_parameter = instance["parameter"]
        baud = int(self.plugin_setup.get("baud", self.OPTIONS["baud"]["default"]))
        instance_parameter["DIVIDER"] = self.system_setup["speed"] // baud // 2 - 1
        return instances


