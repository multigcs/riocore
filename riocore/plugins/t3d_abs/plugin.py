from riocore.plugins import PluginBase


class Plugin(PluginBase):
    def setup(self):
        self.NAME = "t3d_abs"
        self.INFO = "serial abs-encoder hltnc t3d"
        self.DESCRIPTION = """
abs-encoder over rs485

17bit Absolute

red   5V
black GND
blue  PS+ ?
green PS- ?

"""
        self.KEYWORDS = "absolute angle bldc hltnc_t3d A6"
        self.ORIGIN = ""
        self.EXPERIMENTAL = True
        self.VERILOGS = ["t3d_abs.v", "uart_baud.v", "uart_rx.v", "uart_tx.v"]
        self.OPTIONS = {
            "delay": {
                "default": 3,
                "type": int,
                "min": 1,
                "max": 100,
                "unit": "clocks",
                "description": "clock delay for next manchester bit",
            },
            "delay_next": {
                "default": 4,
                "type": int,
                "min": 1,
                "max": 100,
                "unit": "clocks",
                "description": "clock delay for center of the next manchester bit",
            },
        }
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
            "debug_bit": {
                "direction": "output",
                "optional": True,
            },
        }
        self.INTERFACE = {
            "angle": {
                "size": 16,
                "direction": "input",
            },
            "position": {
                "size": 32,
                "direction": "input",
            },
            "csum": {
                "size": 8,
                "direction": "input",
            },
        }
        self.SIGNALS = {
            "angle": {
                "direction": "input",
                "format": "d",
            },
            "position": {
                "direction": "input",
                "format": "d",
            },
            "csum": {
                "direction": "input",
                "format": "0.3f",
            },
        }

    def gateware_instances(self):
        instances = self.gateware_instances_base()
        instance = instances[self.instances_name]
        instance_parameter = instance["parameter"]
        instance_parameter["ClkFrequency"] = self.system_setup["speed"]
        return instances

    def convert(self, signal_name, signal_setup, value):
        if signal_name == "angle":
            return value * 360.0 / 65536
        return value
