import os
from struct import *

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
                "description": "1. ADC channel",
            },
            "adc2": {
                "size": 16,
                "direction": "input",
                "multiplexed": True,
                "description": "2. ADC channel",
            },
            "adc3": {
                "size": 16,
                "direction": "input",
                "multiplexed": True,
                "description": "3. ADC channel",
            },
            "adc4": {
                "size": 16,
                "direction": "input",
                "multiplexed": True,
                "description": "4. ADC channel",
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
        self.DESCRIPTION = """to read analog signals from the iceWerx-board

Range: 0-3.3V -> 0-1024

https://eu.robotshop.com/de/products/devantech-icewerx-ice40-hx8k-fpga

should work also with the iceFUN board

        """


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
