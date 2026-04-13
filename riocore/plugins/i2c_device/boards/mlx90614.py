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

    def __init__(self, parent, system_setup=None):
        self.system_setup = system_setup or {}
        self.name = parent.instances_name
        self.INTERFACE = {
            "ambiente": {
                "size": 16,
                "direction": "input",
                "multiplexed": True,
            },
            "object": {
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
            "object": {
                "direction": "input",
                "format": "0.1f",
                "unit": "°C",
            },
            "ambiente": {
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
                "stop": True,
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
                "stop": True,
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
                "stop": True,
            },
            {
                "mode": "delay",
                "ms": 0.5,
            },
        ]
        self.PINDEFAULTS = {
            "I2C": {"direction": "output", "edge": "target", "pos": [65, 15], "type": ["I2C"], "bus": True},
            "I2C:OUT": {"direction": "output", "edge": "source", "pos": [65, 40], "type": ["PASSTHROUGH"], "bus": True, "pintype": "PASSTHROUGH", "source": "I2C"},
        }

    def convert_c(self, signal_name, signal_setup):
        if signal_name == "valid":
            return ""
        return """
        value = value * 0.02 - 273.15;
        """
