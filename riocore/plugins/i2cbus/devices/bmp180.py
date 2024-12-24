

class i2c_device:
    MEASURMENT_REG = "8'hF4"
    TEMPERATURE_CTRL = "8'h2E"

    def __init__(self, setup):
        self.name = setup["name"]
        self.addr = setup["address"]
        self.addresses = ["8'b11101110"]
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
        self.PARAMS = {
            f"{self.name.upper()}_ADDR": self.addr,
        }

        self.INITS = {}

        self.STEPS = [
            #{
            #    "mode": "write",
            #    "value": f"{{{self.MEASURMENT_REG}, {self.TEMPERATURE_CTRL}}}",
            #    "bytes": 2,
            #},
            {
                "mode": "write",
                "value": self.TEMPERATURE_CTRL,
                "bytes": 1,
            },
            {
                "mode": "read",
                "var": f"{self.name}_temp",
                "bytes": 2,
            },
        ]

