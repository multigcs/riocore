from riocore.plugins import PluginBase


class Plugin(PluginBase):
    def setup(self):
        self.NAME = "tm1638b8s7l8"
        self.INFO = "7segment display with buttons"
        self.DESCRIPTION = "with this plugin, you can use cheap TM1638 boards with LED's/Switches and 7segment displays as control interface for LinuxCNC (JOG/DRO)"
        self.KEYWORDS = "display info status keyboard buttons"
        self.ORIGIN = ""
        self.VERILOGS = ["tm1638b8s7l8.v"]
        self.PINDEFAULTS = {
            "sel": {
                "direction": "output",
                "invert": False,
                "pull": None,
                "description": "Select-Pin (STB)",
            },
            "sclk": {
                "direction": "output",
                "invert": False,
                "pull": None,
                "description": "Clock-Pin (CLK)",
            },
            "data": {
                "direction": "inout",
                "invert": False,
                "pull": None,
                "description": "Data-Pin (DIO)",
            },
        }
        self.INTERFACE = {
            "sw0": {
                "size": 1,
                "direction": "input",
                "multiplexed": True,
            },
            "sw1": {
                "size": 1,
                "direction": "input",
                "multiplexed": True,
            },
            "sw2": {
                "size": 1,
                "direction": "input",
                "multiplexed": True,
            },
            "sw3": {
                "size": 1,
                "direction": "input",
                "multiplexed": True,
            },
            "sw4": {
                "size": 1,
                "direction": "input",
                "multiplexed": True,
            },
            "sw5": {
                "size": 1,
                "direction": "input",
                "multiplexed": True,
            },
            "sw6": {
                "size": 1,
                "direction": "input",
                "multiplexed": True,
            },
            "sw7": {
                "size": 1,
                "direction": "input",
                "multiplexed": True,
            },
            "led0": {
                "size": 1,
                "direction": "output",
                "multiplexed": True,
            },
            "led1": {
                "size": 1,
                "direction": "output",
                "multiplexed": True,
            },
            "led2": {
                "size": 1,
                "direction": "output",
                "multiplexed": True,
            },
            "led3": {
                "size": 1,
                "direction": "output",
                "multiplexed": True,
            },
            "led4": {
                "size": 1,
                "direction": "output",
                "multiplexed": True,
            },
            "led5": {
                "size": 1,
                "direction": "output",
                "multiplexed": True,
            },
            "led6": {
                "size": 1,
                "direction": "output",
                "multiplexed": True,
            },
            "led7": {
                "size": 1,
                "direction": "output",
                "multiplexed": True,
            },
            "number1": {
                "size": 24,
                "direction": "output",
                "multiplexed": True,
            },
            "number2": {
                "size": 8,
                "direction": "output",
                "multiplexed": True,
            },
        }
        self.SIGNALS = {
            "sw0": {
                "direction": "input",
                "bool": True,
            },
            "sw1": {
                "direction": "input",
                "bool": True,
            },
            "sw2": {
                "direction": "input",
                "bool": True,
            },
            "sw3": {
                "direction": "input",
                "bool": True,
            },
            "sw4": {
                "direction": "input",
                "bool": True,
            },
            "sw5": {
                "direction": "input",
                "bool": True,
            },
            "sw6": {
                "direction": "input",
                "bool": True,
            },
            "sw7": {
                "direction": "input",
                "bool": True,
            },
            "led0": {
                "direction": "output",
                "bool": True,
            },
            "led1": {
                "direction": "output",
                "bool": True,
            },
            "led2": {
                "direction": "output",
                "bool": True,
            },
            "led3": {
                "direction": "output",
                "bool": True,
            },
            "led4": {
                "direction": "output",
                "bool": True,
            },
            "led5": {
                "direction": "output",
                "bool": True,
            },
            "led6": {
                "direction": "output",
                "bool": True,
            },
            "led7": {
                "direction": "output",
                "bool": True,
            },
            "number1": {
                "min": -6500.0,
                "max": 6500.0,
                "direction": "output",
                "description": "last 6 digits (-6500.0 -> 6500.0)",
            },
            "number2": {
                "min": 0,
                "max": 99,
                # "hal_type": "u32",
                "direction": "output",
                "description": "first 2 digits (0 -> 99)",
            },
        }
        self.OPTIONS = {
            "speed": {
                "default": 1000000,
                "type": int,
                "description": "Data-clock",
            },
        }
        speed = self.plugin_setup.get("speed", self.option_default("speed"))
        self.TIMING_CONSTRAINTS = {
            "mclk": speed,
        }

    def gateware_instances(self):
        instances = self.gateware_instances_base()
        instance = instances[self.instances_name]
        instance["predefines"]
        instance_parameter = instance["parameter"]
        instance["arguments"]

        speed = self.plugin_setup.get("speed", self.option_default("speed"))
        divider = self.system_setup["speed"] // speed // 5
        instance_parameter["DIVIDER"] = divider
        return instances

    def convert(self, signal_name, signal_setup, value):
        if signal_name == "number1":
            value = value * 10.0
        return value

    def convert_c(self, signal_name, signal_setup):
        if signal_name == "number1":
            return """
            value = value * 10.0;
            """
        return ""
