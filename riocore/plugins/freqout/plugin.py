from riocore.plugins import PluginBase


class Plugin(PluginBase):
    def setup(self):
        self.NAME = "freqout"
        self.VERILOGS = ["freqout.v"]
        self.PINDEFAULTS = {
            "freq": {
                "direction": "output",
                "invert": False,
                "pullup": False,
            },
        }
        self.INTERFACE = {
            "frequency": {
                "size": 32,
                "direction": "output",
            },
        }
        self.SIGNALS = {
            "frequency": {
                "direction": "output",
                "min": 0,
                "max": 1000000,
            },
        }

    def gateware_instances(self):
        instances = self.gateware_instances_base()

        instance = instances[self.instances_name]
        instance_predefines = instance["predefines"]
        instance_parameter = instance["parameter"]
        instance_arguments = instance["arguments"]

        instance_arguments["disabled"] = "ERROR"

        return instances

    def convert(self, signal_name, signal_setup, value):
        if value != 0:
            value = self.system_setup["speed"] / value
        return value

    def convert_c(self, signal_name, signal_setup):
        return """
        if (value != 0) {
            value = OSC_CLOCK / value;
        }
        """
