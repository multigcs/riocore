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
            "power": {
                "size": 16,
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
                "scale": 10.0,
                "unit": "W",
            },
            "state": {
                "direction": "input",
                "format": "",
                "unit": "",
                "mapping": {
                    0: "UNDEFINED",
                    1: "IDLE",
                    2: "STARTUP_SEQUENCE",
                    3: "FULL_CALIBRATION_SEQUENCE",
                    4: "MOTOR_CALIBRATION",
                    5: "???",
                    6: "ENCODER_INDEX_SEARCH",
                    7: "ENCODER_OFFSET_CALIBRATION",
                    8: "CLOSED_LOOP_CONTROL",
                    9: "LOCKIN_SPIN",
                    10: "ENCODER_DIR_FIND",
                    11: "HOMING",
                    12: "ENCODER_HALL_POLARITY_CALIBRATION",
                    13: "ENCODER_HALL_PHASE_CALIBRATION",
                }
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
        instance_parameter["DIVIDER"] = self.system_setup["speed"] // baud // 2 - 1
        return instances


