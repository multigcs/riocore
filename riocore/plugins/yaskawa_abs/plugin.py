from riocore.plugins import PluginBase


class Plugin(PluginBase):
    def setup(self):
        self.NAME = "yaskawa_abs"
        self.INFO = "serial abs-encoder"
        self.DESCRIPTION = """
abs-encoder over rs485

angle scale: 16bit (65536)
position scale: 17bit (131072)

protocol in short:
    * RS485
    * manchester code
    * stuffing bit (after 5x1)
    * 16bit checksum

very time critical
on TangNano9k:
 "speed": "32400000",
 parameter DELAY=3, parameter DELAY_NEXT=4

"""
        self.KEYWORDS = "absolute angle bldc"
        self.ORIGIN = ""
        self.EXPERIMENTAL = True
        self.VERILOGS = ["yaskawa_abs.v"]
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
            "rx_synced": {
                "direction": "output",
                "optional": True,
            },
        }
        self.INTERFACE = {
            "batt_error": {
                "size": 1,
                "direction": "input",
            },
            "temp": {
                "size": 8,
                "direction": "input",
            },
            # "scounter": {
            #     "size": 8,
            #     "direction": "input",
            # },
            # "fcounter": {
            #     "size": 16,
            #     "direction": "input",
            # },
            # "speed": {
            #     "size": 16,
            #     "direction": "input",
            # },
            # "fine_pos": {
            #     "size": 8,
            #     "direction": "input",
            # },
            "angle": {
                "size": 16,
                "direction": "input",
            },
            "position": {
                "size": 32,
                "direction": "input",
            },
            "csum": {
                "size": 16,
                "direction": "input",
            },
            "debug_data": {
                "size": 32,
                "direction": "input",
            },
        }
        self.SIGNALS = {
            "batt_error": {
                "direction": "input",
                "bool": True,
            },
            "temp": {
                "direction": "input",
                "format": "d",
            },
            # "scounter": {
            #     "direction": "input",
            #     "format": "d",
            # },
            # "fcounter": {
            #     "direction": "input",
            #     "format": "d",
            # },
            # "speed": {
            #     "direction": "input",
            #     "format": "d",
            # },
            # "fine_pos": {
            #     "direction": "input",
            #     "format": "d",
            # },
            "angle": {
                "direction": "input",
                "format": "0.2f",
            },
            "position": {
                "direction": "input",
                "format": "0.3f",
            },
            "csum": {
                "direction": "input",
                "format": "d",
            },
            "debug_data": {
                "direction": "input",
                "format": "d",
            },
        }

    def gateware_instances(self):
        instances = self.gateware_instances_base()
        instance = instances[self.instances_name]
        instance_parameter = instance["parameter"]
        instance_parameter["DELAY"] = int(self.plugin_setup.get("delay", self.OPTIONS["delay"]["default"]))
        instance_parameter["DELAY_NEXT"] = int(self.plugin_setup.get("delay_next", self.OPTIONS["delay_next"]["default"]))
        return instances

    def convert(self, signal_name, signal_setup, value):
        if signal_name == "angle":
            # calc angle (0-360°)
            return value * 360 / 65536
        return value

    def convert_c(self, signal_name, signal_setup):
        if signal_name == "angle":
            # calc angle (0-360°)
            return "value = value * 360 / 65536;"
        return ""
