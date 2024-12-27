class i2c_device:
    options = {
        "addresses": ["0x5E", "0x1F"],
    }

    def __init__(self, setup, system_setup={}):
        self.system_setup = system_setup
        self.name = setup["name"]
        self.addr = setup["address"]
        self.INTERFACE = {
            f"{self.name}_x": {
                "size": 16,
                "direction": "input",
                "multiplexed": True,
            },
            f"{self.name}_y": {
                "size": 16,
                "direction": "input",
                "multiplexed": True,
            },
            f"{self.name}_z": {
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
            f"{self.name}_x": {
                "direction": "input",
                "format": "0.1f",
                "unit": "",
            },
            f"{self.name}_y": {
                "direction": "input",
                "format": "0.1f",
                "unit": "",
            },
            f"{self.name}_z": {
                "direction": "input",
                "format": "0.1f",
                "unit": "",
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
                "mode": "writereg",
                "values": [
                    (0x01, 0b0000_0001),  # LowPower
                    (0x03, 0b0000_0000),
                ],
            },
            {
                "mode": "delay",
                "ms": 2,
            },
            {
                "mode": "readreg",
                "register": 0x00,
                "var": f"{self.name}_x",
                "var_set": "{4'd0, data_in[7:0], data_in[11:8]}",
                "bytes": 2,
            },
            {
                "mode": "readreg",
                "register": 0x01,
                "var": f"{self.name}_y",
                "var_set": "{4'd0, data_in[7:0], data_in[11:8]}",
                "bytes": 2,
            },
            {
                "mode": "readreg",
                "register": 0x02,
                "var": f"{self.name}_z",
                "var_set": "{4'd0, data_in[7:0], data_in[11:8]}",
                "bytes": 2,
            },
            {
                "mode": "delay",
                "ms": 2,
            },
        ]

    def convert(self, signal_name, signal_setup, value):
        if signal_name.endswith("_valid"):
            return value
        if value > 2047:
            value = value - 4095
        return value

    def convert_c(self, signal_name, signal_setup):
        if signal_name.endswith("_valid"):
            return ""
        return """
        value = value;
        """
