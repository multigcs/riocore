from riocore.plugins import PluginBase


class Plugin(PluginBase):
    def setup(self):
        self.NAME = "ds18b20"
        self.VERILOGS = ["ds18b20.v"]
        self.PINDEFAULTS = {
            "one_wire": {
                "direction": "inout",
                "invert": False,
                "pull": None,
            },
        }
        self.INTERFACE = {
            "temperature": {
                "size": 16,
                "direction": "input",
            },
        }
        self.SIGNALS = {
            "temperature": {
                "direction": "input",
                "unit": "Hz",
            },
        }
        self.INFO = "1Wire Temperature sensor"
        self.DESCRIPTION = "for cheap 1wire temperature sensor's, only one per pin is supported at the moment"

    def gateware_instances(self):
        instances = self.gateware_instances_base()

        instance = instances[self.instances_name]
        instance["predefines"]
        instance_parameter = instance["parameter"]
        instance["arguments"]

        speed = self.system_setup["speed"] // 1000000 // 2
        instance_parameter["SPEED"] = speed

        return instances
