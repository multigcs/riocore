class i2c_device:
    MLX90614_TA = 0x06
    MLX90614_TOBJ1 = 0x07
    MLX90614_TOBJ2 = 0x08
    options = {
        "addresses": ["0x5A"],
    }

    def __init__(self, setup):
        self.name = setup["name"]
        self.addr = setup["address"]
        self.INTERFACE = {
            f"{self.name}_temp": {
                "size": 16,
                "direction": "input",
            },
        }
        self.SIGNALS = {
            f"{self.name}_temp": {
                "direction": "input",
                "format": "0.1f",
            },
        }
        self.PARAMS = {}
        self.INITS = {}
        self.STEPS = [
            {
                "mode": "write",
                #"value": self.MLX90614_TOBJ1,
                "value": 0x04,
                "bytes": 1,
                "stop": False,
            },
            {
                "mode": "read",
                "var": f"{self.name}_temp",
                "bytes": 2,
            },
        ]

    def convert(self, signal_name, signal_setup, value):
        return value

    def convert_c(self, signal_name, signal_setup):
        return """
        value = value;
        """
