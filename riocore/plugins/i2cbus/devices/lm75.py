class i2c_device:
    def __init__(self, setup):
        self.name = setup["name"]
        self.addr = setup["address"]
        self.INTERFACE = {
            f"{self.name}_in": {
                "size": 16,
                "direction": "input",
            },
        }
        self.SIGNALS = {
            f"{self.name}_in": {
                "direction": "input",
            },
        }
        self.PARAMS = {
            f"{self.name.upper()}_ADDR": self.addr,
        }

        self.INITS = {}

        self.STEPS = {
            "read": {
                "var": f"{self.name}_in",
                "bytes": 2,
            },
        }

    def convert(self, signal_name, signal_setup, value):
        return value / 256.0

    def convert_c(self, signal_name, signal_setup):
        return """
        value = value / 256.0;
        """
