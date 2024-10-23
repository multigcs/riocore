from riocore.plugins import PluginBase


class Plugin(PluginBase):
    def setup(self):
        self.NAME = "irin"
        self.INFO = "IR-Remote input"
        self.DESCRIPTION = "that was just a gimmick, not really useful"
        self.KEYWORDS = "remote control keyboard"
        self.ORIGIN = "https://github.com/douggilliland/MultiComp/blob/master/MultiComp_On_Cyclone%20IV%20VGA%20Card/Card%20docs%20ZRTech-C/3-Example%20Code/5-example_IR_1/ir.v"
        self.VERILOGS = ["irin.v"]
        self.PINDEFAULTS = {
            "ir": {
                "direction": "input",
                "invert": False,
                "pull": None,
            },
        }
        self.INTERFACE = {
            "code": {
                "size": 8,
                "direction": "input",
            },
        }
        self.SIGNALS = {
            "code": {
                "direction": "input",
            },
        }

    def gateware_instances(self):
        instances = self.gateware_instances_base()

        instance = instances[self.instances_name]
        instance["predefines"]
        instance_parameter = instance["parameter"]
        instance["arguments"]

        divider = self.system_setup["speed"] // 1000000 // 2
        instance_parameter["DIVIDER"] = divider

        return instances

    def convert(self, signal_name, signal_setup, value):
        return value
