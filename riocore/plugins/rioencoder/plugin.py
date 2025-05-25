from riocore.plugins import PluginBase


class Plugin(PluginBase):
    def setup(self):
        self.NAME = "rioencoder"
        self.INFO = "serial abs-encoder"
        self.DESCRIPTION = "abs-encoder over rs485 (rx-only)"
        self.KEYWORDS = "absolute ancoder angle bldc"
        self.ORIGIN = ""
        self.VERILOGS = ["rioencoder.v", "uart_baud.v", "uart_rx.v"]
        self.PINDEFAULTS = {
            "rx": {
                "direction": "input",
            },
            "rw": {
                "direction": "output",
                "optional": True,
            },
        }
        self.INTERFACE = {
            "angle": {
                "size": 16,
                "direction": "input",
            },
        }
        self.SIGNALS = {
            "angle": {
                "direction": "input",
            },
        }

    def gateware_instances(self):
        instances = self.gateware_instances_base()
        instance = instances[self.instances_name]
        instance_parameter = instance["parameter"]
        instance_parameter["ClkFrequency"] = self.system_setup["speed"]
        return instances
