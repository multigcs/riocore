from riocore.plugins import PluginBase


class Plugin(PluginBase):
    def setup(self):
        self.NAME = "panasonic_abs"
        self.INFO = "serial abs-encoder"
        self.DESCRIPTION = """
abs-encoder over rs485

for Panasonic and some Bosch/Rexroth Servos with
mfe0017 encoder

FG      Shield      
VCC-    GND     Black
VCC+    5V      White
VB-     GND     Orange
VB+     3.3V    RED
SD+     RS485-A Blue
SD-     RS485-B Brown

Connector:
V+  V-
B-  SD+
B+  SD-  FG

"""
        self.KEYWORDS = "absolute angle bldc panasonic bosch rexroth mfe0017 minas"
        self.ORIGIN = ""
        self.EXPERIMENTAL = True
        self.VERILOGS = ["panasonic_abs.v", "uart_baud.v", "uart_rx.v", "uart_tx.v"]
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
            "tmp1": {
                "size": 8,
                "direction": "input",
            },
            "tmp2": {
                "size": 8,
                "direction": "input",
            },
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
            "debug_data": {
                "size": 32,
                "direction": "input",
            },
            "cmd": {
                "size": 8,
                "direction": "output",
            },
        }
        self.SIGNALS = {
            "tmp1": {
                "direction": "input",
                "format": "d",
            },
            "tmp2": {
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
            "csum": {
                "direction": "input",
                "format": "0.3f",
            },
            "debug_data": {
                "direction": "input",
                "format": "d",
            },
            "cmd": {
                "direction": "output",
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
        # if signal_name == "csum":
        #    print(f"#### {value:032b} {value:d}")

        # if signal_name == "position":
        #    print(f"{value:032b} {(value & 0xFF000000) >> 24} {(value & 0xFF0000) >> 16} {((value & 0xFF00) >> 8)} {(value & 0xFF)}")
        if signal_name == "angle":
            return value * 360.0 / 65536
        return value
