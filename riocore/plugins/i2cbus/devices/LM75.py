class i2c_device:
    def __init__(self, name, addr):
        self.name = name
        self.addr = addr
        self.INTERFACE = {
            f"{name}_in": {
                "size": 16,
                "direction": "input",
            },
        }
        self.SIGNALS = {
            f"{name}_in": {
                "direction": "input",
            },
        }
        self.PARAMS = {
            f"{name.upper()}_ADDR": addr,
        }

        self.INITS = {}

        self.STEPS = {
            "read": {
                "var": f"{name}_in",
                "bytes": 2,
            },
        }

    def convert(self, signal_name, signal_setup, value):
        return value / 256.0

    def convert_c(self, signal_name, signal_setup):
        return """
        value = value / 256.0;
        """
