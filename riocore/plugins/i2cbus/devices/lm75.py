class i2c_device:
    options = {
        "addresses": ["0x48", "0x49", "0x4A", "0x4B", "0x4C", "0x4D", "0x4E", "0x4F"],
    }

    def __init__(self, setup):
        self.name = setup["name"]
        self.addr = setup["address"]
        self.INTERFACE = {
            f"{self.name}_temp": {
                "size": 16,
                "direction": "input",
                "multiplexed": True,
            },
        }
        self.SIGNALS = {
            f"{self.name}_temp": {
                "direction": "input",
                "format": "0.1f",
                "unit": "°C",
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

    def convert(self, signal_name, signal_setup, value):
        return value / 256.0

    def convert_c(self, signal_name, signal_setup):
        return """
        value = value / 256.0;
        """
