class i2c_device:
    def __init__(self, name, addr):
        self.name = name
        self.addr = addr
        self.INTERFACE = {
            f"{name}_in": {
                "size": 8,
                "direction": "input",
            },
            f"{name}_out": {
                "size": 8,
                "direction": "output",
            },
        }
        self.SIGNALS = {
            f"{name}_in": {
                "direction": "input",
                "min": 0,
                "max": 255,
            },
            f"{name}_out": {
                "direction": "output",
                "min": 0,
                "max": 255,
            },
        }
        self.PARAMS = {
            f"{name.upper()}_ADDR": addr,
        }

        self.INITS = {}

        self.STEPS = {
            "write": {
                "var": f"{name}_out",
                "bytes": 1,
            },
            "read": {
                "var": f"{name}_in",
                "bytes": 1,
            },
        }
