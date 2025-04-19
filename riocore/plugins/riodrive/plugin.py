from riocore.plugins import PluginBase


class Plugin(PluginBase):
    def setup(self):
        self.NAME = "riodrive"
        self.INFO = "to control a riodrive via can-bus"
        self.DESCRIPTION = "riodrive is a fork of odrive (3.6)"
        self.KEYWORDS = "canbus odrive"
        self.ORIGIN = ""
        self.TYPE = "joint"

        self.VERILOGS = ["riodrive.v", "canbus_tx.v", "canbus_rx.v"]

        self.OPTIONS = {
            "baud": {
                "default": 250000,
                "type": int,
                "min": 300,
                "max": 10000000,
                "unit": "bit/s",
                "description": "serial baud rate",
            },
            "interval": {
                "default": 500,
                "type": int,
                "min": 100,
                "max": 10000,
                "unit": "Hz",
                "description": "update interval",
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
            "power": {
                "size": 16,
                "direction": "input",
                "description": "",
            },
            "temp": {
                "size": 8,
                "direction": "input",
                "description": "",
            },
            "state": {
                "size": 4,
                "direction": "input",
                "description": "",
            },
            "traj": {
                "size": 1,
                "direction": "input",
                "description": "",
            },
            "mot": {
                "size": 1,
                "direction": "input",
                "description": "",
            },
            "enc": {
                "size": 1,
                "direction": "input",
                "description": "",
            },
            "ctrl": {
                "size": 1,
                "direction": "input",
                "description": "",
            },
            "position": {
                "size": 32,
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
            "power": {
                "direction": "input",
                "format": "0.1f",
                "unit": "W",
            },
            "temp": {
                "direction": "input",
                "format": "0.1f",
                "unit": "°C",
            },
            "state": {
                "direction": "input",
                "format": "",
                "unit": "",
                "mapping": {
                    0: "UNDEFINED",
                    1: "IDLE",
                    2: "STARTUP_SEQUENCE",
                    8: "CLOSED_LOOP_CONTROL",
                    9: "LOCKIN_SPIN",
                    11: "HOMING",
                },
            },
            "traj": {
                "direction": "input",
                "format": "f",
                "unit": "",
                "bool": True,
            },
            "mot": {
                "direction": "input",
                "format": "f",
                "unit": "",
                "bool": True,
            },
            "enc": {
                "direction": "input",
                "format": "f",
                "unit": "",
                "bool": True,
            },
            "ctrl": {
                "direction": "input",
                "format": "f",
                "unit": "",
                "bool": True,
            },
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
        instance_parameter["DIVIDER"] = self.system_setup["speed"] // baud - 1
        interval = int(self.plugin_setup.get("interval", self.OPTIONS["interval"]["default"]))
        instance_parameter["IDIVIDER"] = self.system_setup["speed"] // interval
        return instances

    def convert(self, signal_name, signal_setup, value):
        if signal_name == "power":
            value = value / 10.0
        elif signal_name == "temp":
            value = value / 2.0
        return value

    def convert_c(self, signal_name, signal_setup):
        if signal_name == "power":
            return "value = value / 10.0;"
        elif signal_name == "temp":
            return "value = value / 2.0;"
        return ""
