class i2c_device:
    options = {
        "info": "12-bit DAC",
        "description": "12-Bit Digital-to-Analog Converter with EEPROM Memory",
        "addresses": ["0x60", "0x61", "0x62", "0x63", "0x64", "0x65", "0x66", "0x67"],
    }

    def __init__(self, parent, system_setup=None):
        self.system_setup = system_setup or {}
        self.name = parent.instances_name
        self.INTERFACE = {
            f"{self.name}_voltage": {
                "size": 16,
                "direction": "output",
            },
            f"{self.name}_valid": {
                "size": 1,
                "direction": "input",
                "multiplexed": True,
            },
        }
        self.SIGNALS = {
            f"{self.name}_voltage": {
                "direction": "output",
                "min": 0,
                "max": 3300,
                "format": "0.1f",
                "unit": "mV",
            },
            f"{self.name}_valid": {
                "direction": "input",
                "bool": True,
            },
        }

        self.PARAMS = {}
        self.INITS = []
        self.STEPS = [
            {
                "comment": "write data in fast-mode",
                "mode": "write",
                "value": f"{{4'b0000, {self.name}_voltage[11:0]}}",
                "bytes": 2,
            },
        ]
        self.PINDEFAULTS = {
            "I2C": {"direction": "output", "edge": "target", "pos": [20, 60], "type": ["I2C"], "bus": True},
            "I2C:OUT": {"direction": "output", "edge": "source", "pos": [50, 60], "type": ["PASSTHROUGH"], "bus": True, "pintype": "PASSTHROUGH", "source": "I2C"},
        }

    def convert(self, signal_name, signal_setup, value):
        if signal_name.endswith("_valid"):
            return value
        return value * 4095 / 3300

    def convert_c(self, signal_name, signal_setup):
        if signal_name.endswith("_valid"):
            return ""
        return """
        value = value * 4095 / 3300;
        """
