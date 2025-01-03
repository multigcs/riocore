class i2c_device:
    MLX90614_TA = 0x06
    MLX90614_TOBJ1 = 0x07
    MLX90614_TOBJ2 = 0x08
    MLX90614_SLEEP_MODE = 0xFF
    MLX90614_SLEEP_MODE_PEC = 0xE8

    options = {
        "info": "ir temperature sensor",
        "description": "works only up to 100kHz",
        "addresses": ["0x5A"],
    }

    def __init__(self, setup, system_setup={}):
        self.system_setup = system_setup
        self.name = setup["name"]
        self.addr = setup["address"]
        self.INTERFACE = {
            f"{self.name}_ambiente": {
                "size": 16,
                "direction": "input",
                "multiplexed": True,
            },
            f"{self.name}_object": {
                "size": 16,
                "direction": "input",
                "multiplexed": True,
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
                "unit": "°C",
            },
            f"{self.name}_ambiente": {
                "direction": "input",
                "format": "0.1f",
                "unit": "°C",
            },
            f"{self.name}_valid": {
                "direction": "input",
                "bool": True,
            },
        }
        self.PARAMS = {}
        self.INITS = [
            {
                "mode": "write",
                "value": "8'h24",
                "bytes": 0,
            },
            {
                "mode": "write",
                "value": "8'h24",
                "bytes": 1,
                "stop": False,
            },
            {
                "mode": "read",
                "var": f"{self.name}_ambiente",
                "var_set": "data_in[15:0]",
                "bytes": 2,
            },
            {
                "mode": "delay",
                "ms": 1,
            },
        ]
        self.STEPS = [
            {
                "mode": "write",
                "value": "8'h06",
                "bytes": 1,
                "stop": False,
            },
            {
                "mode": "read",
                "var": f"{self.name}_ambiente",
                "big_endian": True,
                "bytes": 2,
            },
            {
                "mode": "delay",
                "ms": 0.5,
            },
            {
                "mode": "write",
                "value": "8'h07",
                "bytes": 1,
                "stop": False,
            },
            {
                "mode": "read",
                "var": f"{self.name}_object",
                "big_endian": True,
                "bytes": 2,
            },
            {
                "mode": "delay",
                "ms": 0.5,
            },
        ]

    def convert(self, signal_name, signal_setup, value):
        if signal_name.endswith("_valid"):
            return value
        return value * 0.02 - 273.15

    def convert_c(self, signal_name, signal_setup):
        if signal_name.endswith("_valid"):
            return ""
        return """
        value = value * 0.02 - 273.15;
        """
