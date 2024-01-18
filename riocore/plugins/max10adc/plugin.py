from riocore.plugins import PluginBase


class Plugin(PluginBase):
    def setup(self):
        self.NAME = "max10adc"
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
