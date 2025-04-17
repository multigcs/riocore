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
            "oclk": {
                "direction": "output",
            },
            "tx": {
                "direction": "output",
            },
            "rx": {
                "direction": "input",
            },
        }
        self.INTERFACE = {
            "din": {
                "size": 32,
                "direction": "input",
                "description": "",
            },
            "dout": {
                "size": 32,
                "direction": "output",
                "description": "",
            },
        }
        self.SIGNALS = {
            "din": {
                "direction": "input",
                "format": "0.2f",
                "unit": "",
            },
            "dout": {
                "direction": "output",
                "min": -10,
                "max": 10,
                "format": "0.2f",
                "unit": "",
            },
        }

    def gateware_instances(self):
        instances = self.gateware_instances_base()
        instance = instances[self.instances_name]
        instance_parameter = instance["parameter"]
        baud = int(self.plugin_setup.get("baud", self.OPTIONS["baud"]["default"]))
        instance_parameter["DIVIDER"] = self.system_setup["speed"] // baud // 2 - 1
        return instances

    def convert(self, signal_name, signal_setup, value):
        if signal_name  == "din":
            value = unpack(">f", bytes(list(pack("<i", value))))[0]
        elif signal_name  == "dout":
                value = unpack("<i", bytes(list(pack(">f", value))))[0]
        return value

