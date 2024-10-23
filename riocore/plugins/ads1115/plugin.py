import math
from riocore.plugins import PluginBase


class Plugin(PluginBase):
    def setup(self):
        self.NAME = "ads1115"
        self.INFO = "4-channel adc via I2C"
        self.DESCRIPTION = "to read analog signals with cheap ads1115 chips"
        self.KEYWORDS = "adc analog temperature ampere voltage"
        self.ORIGIN = "https://learn.lushaylabs.com/i2c-adc-micro-procedures/#the-i2c-protocol"
        self.VERILOGS = ["ads1115.v"]
        self.PINDEFAULTS = {
            "sda": {
                "direction": "inout",
                "invert": False,
                "pull": "up",
            },
            "scl": {
                "direction": "output",
                "invert": False,
                "pull": "up",
            },
        }
        self.INTERFACE = {
            "adc0": {
                "size": 16,
                "direction": "input",
                "multiplexed": True,
            },
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
        }
        self.SIGNALS = {
            "adc0": {
                "direction": "input",
                "format": "0.3f",
                "unit": "Volt",
            },
            "adc1": {
                "direction": "input",
                "format": "0.3f",
                "unit": "Volt",
            },
            "adc2": {
                "direction": "input",
                "format": "0.3f",
                "unit": "Volt",
            },
            "adc3": {
                "direction": "input",
                "format": "0.3f",
                "unit": "Volt",
            },
        }
        self.OPTIONS = {
            "address": {
                "default": "1",
                "type": "select",
                "options": ["0", "1"],
                "description": "I2C-Address",
            },
            "sensor0": {
                "default": "Voltage",
                "type": "select",
                "options": ["Voltage", "NTC"],
                "description": "Sensor-Type",
            },
            "sensor1": {
                "default": "Voltage",
                "type": "select",
                "options": ["Voltage", "NTC"],
                "description": "Sensor-Type",
            },
            "sensor2": {
                "default": "Voltage",
                "type": "select",
                "options": ["Voltage", "NTC"],
                "description": "Sensor-Type",
            },
            "sensor3": {
                "default": "Voltage",
                "type": "select",
                "options": ["Voltage", "NTC"],
                "description": "Sensor-Type",
            },
        }
        for sn in range(4):
            stype = self.plugin_setup.get(f"sensor{sn}", self.option_default(f"sensor{sn}"))
            if stype == "NTC":
                self.SIGNALS[f"adc{sn}"]["format"] = "0.1f"
                self.SIGNALS[f"adc{sn}"]["unit"] = "°C"
            else:
                self.SIGNALS[f"adc{sn}"]["format"] = "0.3f"
                self.SIGNALS[f"adc{sn}"]["unit"] = "Volt"

    def gateware_instances(self):
        instances = self.gateware_instances_base()
        instance = instances[self.instances_name]
        instance["predefines"]
        instance_parameter = instance["parameter"]
        instance["arguments"]
        address = self.plugin_setup.get("address", self.option_default("address"))
        instance_parameter["ADDRESS"] = f"7'b100100{address}"
        return instances

    def convert(self, signal_name, signal_setup, value):
        channel = signal_name[-1]
        sensor = self.plugin_setup.get(f"sensor{channel}", self.OPTIONS[f"sensor{channel}"]["default"])
        value /= 1000.0
        if sensor == "NTC":
            Rt = 10.0 * value / (3.3 - value)
            if Rt == 0.0:
                value = -999.0
            else:
                tempK = 1.0 / (math.log(Rt / 10.0) / 3950.0 + 1.0 / (273.15 + 25.0))
                tempC = tempK - 273.15
                value = tempC
        return value
