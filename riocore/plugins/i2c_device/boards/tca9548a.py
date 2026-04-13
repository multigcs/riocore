class i2c_device:
    options = {
        "info": "i2c multiplexer",
        "description": "",
        "addresses": ["0x70", "0x71", "0x72", "0x73", "0x74", "0x75", "0x76", "0x77"],
        "multiplexer": True,
    }

    def __init__(self, parent, system_setup=None):
        self.system_setup = system_setup or {}
        self.name = parent.instances_name
        self.INTERFACE = {}
        self.SIGNALS = {}
        self.PARAMS = {}
        self.INITS = []
        self.STEPS = []
        self.PINDEFAULTS = {
            "I2C": {"direction": "output", "edge": "target", "pos": [8, 30], "type": ["I2C"], "bus": True},
            "I2C:OUT0": {"direction": "output", "edge": "source", "pos": [8, 100], "type": ["PASSTHROUGH"], "bus": True, "pintype": "PASSTHROUGH", "source": "I2C", "busid": 0},
            "I2C:OUT1": {"direction": "output", "edge": "source", "pos": [8, 123], "type": ["PASSTHROUGH"], "bus": True, "pintype": "PASSTHROUGH", "source": "I2C", "busid": 1},
            "I2C:OUT2": {"direction": "output", "edge": "source", "pos": [91, 134], "type": ["PASSTHROUGH"], "bus": True, "pintype": "PASSTHROUGH", "source": "I2C", "busid": 2},
            "I2C:OUT3": {"direction": "output", "edge": "source", "pos": [91, 111], "type": ["PASSTHROUGH"], "bus": True, "pintype": "PASSTHROUGH", "source": "I2C", "busid": 3},
            "I2C:OUT4": {"direction": "output", "edge": "source", "pos": [91, 88], "type": ["PASSTHROUGH"], "bus": True, "pintype": "PASSTHROUGH", "source": "I2C", "busid": 4},
            "I2C:OUT5": {"direction": "output", "edge": "source", "pos": [91, 65], "type": ["PASSTHROUGH"], "bus": True, "pintype": "PASSTHROUGH", "source": "I2C", "busid": 5},
            "I2C:OUT6": {"direction": "output", "edge": "source", "pos": [91, 42], "type": ["PASSTHROUGH"], "bus": True, "pintype": "PASSTHROUGH", "source": "I2C", "busid": 6},
            "I2C:OUT7": {"direction": "output", "edge": "source", "pos": [91, 18], "type": ["PASSTHROUGH"], "bus": True, "pintype": "PASSTHROUGH", "source": "I2C", "busid": 7},
        }

    def convert_c(self, signal_name, signal_setup):
        if signal_name == "valid":
            return ""
        return """
        value = value / 256.0;
        """
