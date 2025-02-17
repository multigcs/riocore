from riocore.plugins import PluginBase


class Plugin(PluginBase):
    def setup(self):
        self.NAME = "max10adc"
        self.INFO = "MAX10 ADC inputs"
        self.DESCRIPTION = "only usable for the max10 fpga boards"
        self.KEYWORDS = "analog adc voltage ampere"
        self.ORIGIN = "ACDS version 16.0 211"
        self.LIMITATIONS = {
            "family": ["MAX 10"],
            "toolchains": ["quartus"],
        }
        self.VERILOGS = ["max10adc.v"]
        self.INTERFACE = {
            "adc0": {
                "size": 16,
                "direction": "input",
            },
            "adc1": {
                "size": 16,
                "direction": "input",
            },
            "adc2": {
                "size": 16,
                "direction": "input",
            },
            "adc3": {
                "size": 16,
                "direction": "input",
            },
            "adc4": {
                "size": 16,
                "direction": "input",
            },
            "adc5": {
                "size": 16,
                "direction": "input",
            },
            "adc6": {
                "size": 16,
                "direction": "input",
            },
            "adc7": {
                "size": 16,
                "direction": "input",
            },
        }
        self.SIGNALS = {
            "adc0": {
                "direction": "input",
            },
            "adc1": {
                "direction": "input",
            },
            "adc2": {
                "direction": "input",
            },
            "adc3": {
                "direction": "input",
            },
            "adc4": {
                "direction": "input",
            },
            "adc5": {
                "direction": "input",
            },
            "adc6": {
                "direction": "input",
            },
            "adc7": {
                "direction": "input",
            },
        }
