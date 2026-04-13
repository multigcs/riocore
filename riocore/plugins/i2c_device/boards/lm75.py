class i2c_device:
    options = {
        "info": "temperature sensor",
        "description": "",
        "addresses": ["0x48", "0x49", "0x4A", "0x4B", "0x4C", "0x4D", "0x4E", "0x4F"],
    }

    def __init__(self, parent, system_setup=None):
        self.system_setup = system_setup or {}
        self.name = parent.instances_name
        self.INTERFACE = {
            "temp": {
                "size": 16,
                "direction": "input",
                "multiplexed": True,
            },
            "valid": {
                "size": 1,
                "direction": "input",
                "multiplexed": True,
            },
        }
        self.SIGNALS = {
            "temp": {
                "direction": "input",
                "format": "0.1f",
                "unit": "°C",
            },
            "valid": {
                "direction": "input",
                "bool": True,
            },
        }
        self.PARAMS = {}
        self.INITS = []
        self.STEPS = [
            {
                "mode": "read",
                "var": f"{self.name}_temp",
                "bytes": 2,
            },
        ]
        self.PINDEFAULTS = {
            "I2C": {"direction": "output", "edge": "target", "pos": [20, 50], "type": ["I2C"], "bus": True},
            "I2C:OUT": {"direction": "output", "edge": "source", "pos": [36, 50], "type": ["PASSTHROUGH"], "bus": True, "pintype": "PASSTHROUGH", "source": "I2C"},
        }

    def convert_c(self, signal_name, signal_setup):
        if signal_name == "valid":
            return ""
        return """
        value = value / 256.0;
        """
