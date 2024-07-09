import os
from struct import *

from riocore.checksums import crc8, crc16
from riocore.plugins import PluginBase

class Plugin(PluginBase):
    def setup(self):
        self.NAME = "icewerxadc"
        self.VERILOGS = ["icewerxadc.v", "uart_baud.v", "uart_rx.v", "uart_tx.v"]
        self.PINDEFAULTS = {
            "tx": {
                "direction": "output",
            },
            "rx": {
                "direction": "input",
            }
        }
        self.INTERFACE = {
            "adc1": {
                "size": 16,
                "direction": "input",
                "multiplexed": True,
            },
            "adc2": {
                "size": 16,
                "direction": "input",
                "multiplexed": True,
            },
            "adc3": {
                "size": 16,
                "direction": "input",
                "multiplexed": True,
            },
            "adc4": {
                "size": 16,
                "direction": "input",
                "multiplexed": True,
            },
        }
        self.SIGNALS = {
            "adc1": {
                "direction": "input",
                "format": "0.2f",
                "unit": "Volt",
            },
            "adc2": {
                "direction": "input",
                "format": "0.2f",
                "unit": "Volt",
            },
            "adc3": {
                "direction": "input",
                "format": "0.2f",
                "unit": "Volt",
            },
            "adc4": {
                "direction": "input",
                "format": "0.2f",
                "unit": "Volt",
            },
        }
        self.INFO = "4-channel adc of the iceWerx-board"
        self.DESCRIPTION = "to read analog signals from the iceWerx-board"


    def gateware_instances(self):
        instances = self.gateware_instances_base()
        instance = instances[self.instances_name]
        instance_predefines = instance["predefines"]
        instance_parameter = instance["parameter"]
        instance_arguments = instance["arguments"]
        instance_parameter["ClkFrequency"] = self.system_setup["speed"]
        return instances

    def convert(self, signal_name, signal_setup, value):
        value = value / 310.3030303030303
        return value

    def convert_c(self, signal_name, signal_setup):
        return """
        value = value / 310.3030303030303;
        """
