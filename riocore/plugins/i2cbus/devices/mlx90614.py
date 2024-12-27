class i2c_device:
    MLX90614_TA = 0x06
    MLX90614_TOBJ1 = 0x07
    MLX90614_TOBJ2 = 0x08
    MLX90614_SLEEP_MODE = 0xFF
    MLX90614_SLEEP_MODE_PEC = 0xE8

    options = {
        "addresses": ["0x5A"],
    }

    def __init__(self, setup):
        self.name = setup["name"]
        self.addr = setup["address"]
        self.INTERFACE = {
            f"{self.name}_ambiente": {
                "size": 16,
                "direction": "input",
            },
            f"{self.name}_object": {
                "size": 16,
                "direction": "input",
            },
            f"{self.name}_valid": {
                "size": 1,
                "direction": "input",
            },
        }
        self.SIGNALS = {
            f"{self.name}_object": {
                "direction": "input",
                "format": "0.1f",
            },
            f"{self.name}_ambiente": {
                "direction": "input",
                "format": "0.1f",
            },
            f"{self.name}_valid": {
                "direction": "input",
                "bool": True,
            },
        }
        self.PARAMS = {}
        self.INITS = [
            {
                "mode": "writereg",
                "values": [
                    (self.MLX90614_SLEEP_MODE, self.MLX90614_SLEEP_MODE_PEC),
                ],
            },
            {
                "mode": "wakeup",
            },
        ]
        self.STEPS = [
            {
                "mode": "readreg",
                "register": self.MLX90614_TA,
                "var": f"{self.name}_ambiente",
                "big_endian": True,
                "bytes": 2,
            },
            {
                "mode": "readreg",
                "register": self.MLX90614_TOBJ1,
                "var": f"{self.name}_object",
                "big_endian": True,
                "bytes": 2,
            },
        ]

    def convert(self, signal_name, signal_setup, value):
        if signal_name.endswith("_valid"):
            return value
        return value

    def convert_c(self, signal_name, signal_setup):
        if signal_name.endswith("_valid"):
            return ""
        return """
        value = value;
        """
