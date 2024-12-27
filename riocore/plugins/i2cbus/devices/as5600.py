class i2c_device:
    options = {
        "addresses": ["0x36"],
    }

    def __init__(self, setup, system_setup={}):
        self.system_setup = system_setup
        self.name = setup["name"]
        self.addr = setup["address"]
        self.INTERFACE = {
            f"{self.name}_val": {
                "size": 16,
                "direction": "input",
            },
            f"{self.name}_valid": {
                "size": 1,
                "direction": "input",
            },
        }
        self.SIGNALS = {
            f"{self.name}_val": {
                "direction": "input",
                "format": "0.1f",
            },
            f"{self.name}_valid": {
                "direction": "input",
                "bool": True,
            },
        }
        self.PARAMS = {}

        self.INITS = {}

        self.STEPS = [
            {
                "mode": "write",
                "value": "8'd14",
                "bytes": 1,
            },
            {
                "mode": "read",
                "var": f"{self.name}_val",
                "var_set": "{3'd0, data_in[11:0]}",
                "bytes": 2,
            },
        ]

    def convert(self, signal_name, signal_setup, value):
        if signal_name.endswith("_valid"):
            return value
        return value * 360 / 4096

    def convert_c(self, signal_name, signal_setup):
        if signal_name.endswith("_valid"):
            return ""
        return """
        value = value * 360 / 4096;
        """
