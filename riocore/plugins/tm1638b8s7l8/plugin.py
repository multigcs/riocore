from riocore.plugins import PluginBase


class Plugin(PluginBase):
    def setup(self):
        self.NAME = "tm1638b8s7l8"
        self.VERILOGS = ["tm1638b8s7l8.v"]
        self.PINDEFAULTS = {
            "sel": {
                "direction": "output",
                "invert": False,
                "pullup": False,
            },
            "sclk": {
                "direction": "output",
                "invert": False,
                "pullup": False,
            },
            "data": {
                "direction": "inout",
                "invert": False,
                "pullup": False,
            },
        }
        self.INTERFACE = {
            "sw0": {
                "size": 1,
                "direction": "input",
            },
            "sw1": {
                "size": 1,
                "direction": "input",
            },
            "sw2": {
                "size": 1,
                "direction": "input",
            },
            "sw3": {
                "size": 1,
                "direction": "input",
            },
            "sw4": {
                "size": 1,
                "direction": "input",
            },
            "sw5": {
                "size": 1,
                "direction": "input",
            },
            "sw6": {
                "size": 1,
                "direction": "input",
            },
            "sw7": {
                "size": 1,
                "direction": "input",
            },
            "led0": {
                "size": 1,
                "direction": "output",
            },
            "led1": {
                "size": 1,
                "direction": "output",
            },
            "led2": {
                "size": 1,
                "direction": "output",
            },
            "led3": {
                "size": 1,
                "direction": "output",
            },
            "led4": {
                "size": 1,
                "direction": "output",
            },
            "led5": {
                "size": 1,
                "direction": "output",
            },
            "led6": {
                "size": 1,
                "direction": "output",
            },
            "led7": {
                "size": 1,
                "direction": "output",
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
                "min": -65000,
                "max": 65000,
                "direction": "output",
            },
            "number2": {
                "min": 0,
                "max": 99,
                "hal_type": "u32",
                "direction": "output",
            },
        }

    def gateware_instances(self):
        instances = self.gateware_instances_base()
        instance = instances[self.instances_name]
        instance_predefines = instance["predefines"]
        instance_parameter = instance["parameter"]
        instance_arguments = instance["arguments"]
        # example
        # frequency = int(self.plugin_setup.get("frequency", 100))
        # divider = self.system_setup["speed"] // frequency
        # instance_parameter["DIVIDER"] = divider
        # instance_parameter["DIVIDER"] = self.plugin_setup.get("divider", "1000")
        return instances
