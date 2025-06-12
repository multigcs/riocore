from riocore.plugins import PluginBase


class Plugin(PluginBase):
    def setup(self):
        self.NAME = "t3d_abs"
        self.INFO = "serial abs-encoder hltnc t3d"
        self.DESCRIPTION = """
abs-encoder over rs485

17bit Absolute

Firewire-Connector:
* 1 PS+
* 2 PS-
* 3 NC
* 4 NC
* 5 5V
* 6 GND

"""
        self.KEYWORDS = "absolute angle bldc hltnc_t3d A6"
        self.ORIGIN = ""
        self.EXPERIMENTAL = True
        self.VERILOGS = ["t3d_abs.v", "uart_baud.v", "uart_rx.v", "uart_tx.v"]
        self.OPTIONS = {}
        self.PINDEFAULTS = {
            "rx": {
                "direction": "input",
            },
            "tx": {
                "direction": "output",
            },
            "tx_enable": {
                "direction": "output",
            },
        }
        self.INTERFACE = {
            "angle": {
                "size": 16,
                "direction": "input",
            },
            "revs": {
                "size": 32,
                "direction": "input",
            },
            "angle16": {
                "size": 16,
                "direction": "input",
            },
            "angle": {
                "size": 32,
                "direction": "input",
            },
        }
        self.SIGNALS = {
            "revs": {
                "direction": "input",
                "format": "d",
            },
            "angle16": {
                "direction": "input",
                "format": "d",
            },
            "angle": {
                "direction": "input",
                "format": "d",
            },
            "position": {
                "direction": "input",
                "format": "d",
            },
        }

    def gateware_instances(self):
        instances = self.gateware_instances_base()
        instance = instances[self.instances_name]
        instance_parameter = instance["parameter"]
        instance_parameter["ClkFrequency"] = self.system_setup["speed"]
        return instances

    def convert(self, signal_name, signal_setup, value):
        if signal_name == "angle16":
            value = value * 360.0 / 65536
        elif signal_name == "angle":
            self.SIGNALS["position"]["value"] = self.SIGNALS["revs"]["value"] * 131072 + value
        return value
