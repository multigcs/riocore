class i2c_device:
    def __init__(self, setup):
        self.name = setup["name"]
        self.addr = setup["address"]
        self.addresses = ["8'b01101100"]
        self.INTERFACE = {
            f"{self.name}_val": {
                "size": 16,
                "direction": "input",
            },
        }
        self.SIGNALS = {
            f"{self.name}_val": {
                "direction": "input",
                "format": "0.1f",
            },
        }
        self.PARAMS = {
            f"{self.name.upper()}_ADDR": self.addr,
        }

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
        return value / 256.0

    def convert_c(self, signal_name, signal_setup):
        return """
        value = value / 256.0;
        """
