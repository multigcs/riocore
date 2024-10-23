from riocore.plugins import PluginBase


class Plugin(PluginBase):
    def setup(self):
        self.NAME = "blink"
        self.INFO = "blinking output pin"
        self.DESCRIPTION = "outputs a fixed frequency / was used to indicate that the FPGA is runing / no control signals"
        self.KEYWORDS = "led blinking"
        self.ORIGIN = ""
        self.VERILOGS = ["blink.v"]
        self.PINDEFAULTS = {
            "led": {
                "direction": "output",
                "drive": 8,
            },
        }
        self.OPTIONS = {
            "frequency": {
                "default": 1.0,
                "type": float,
                "unit": "Hz",
                "description": "blink frequency in Hz",
            },
        }

    def gateware_instances(self):
        instances = self.gateware_instances_base()
        instance = instances[self.instances_name]
        instance["predefines"]
        instance_parameter = instance["parameter"]
        instance["arguments"]
        freq = int(self.plugin_setup.get("frequency", self.OPTIONS["frequency"]["default"]))
        divider = self.system_setup["speed"] // freq // 2
        instance_parameter["DIVIDER"] = divider
        return instances
