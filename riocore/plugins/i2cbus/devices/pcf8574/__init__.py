class i2c_device:
    options = {
        "info": "8bit io-expander",
        "description": "",
        "addresses": ["0x20", "0x21", "0x22", "0x23", "0x24", "0x25", "0x26", "0x27"],
        "config": {
            "bitvar": {
                "type": bool,
                "description": "use as single bits",
                "default": True,
            },
            "expansion": {
                "type": bool,
                "description": "use as expansion io",
                "default": False,
            },
            "inputs": {
                "type": "bits",
                "min": 0,
                "max": 255,
                "description": "use as input",
                "default": 255,
            },
            "outputs": {
                "type": "bits",
                "min": 0,
                "max": 255,
                "description": "use as output",
                "default": 255,
            },
        },
    }

    def __init__(self, setup, system_setup={}):
        self.system_setup = system_setup
        self.name = setup["name"]
        self.addr = setup["address"]
        self.bitvar = setup.get("bitvar", self.options["config"]["bitvar"]["default"])
        self.inputs = setup.get("inputs", self.options["config"]["inputs"]["default"])
        self.outputs = setup.get("outputs", self.options["config"]["outputs"]["default"])
        self.INTERFACE = {}
        self.SIGNALS = {}
        if self.bitvar:
            setup["data_in"] = []

            # write single bits into data_out byte
            bitlist = []
            for bit in range(8):
                if (1 << bit) & self.outputs:
                    bitlist.append(f"{self.name}_out{bit}")
                else:
                    bitlist.append("1'd1")

            setup["value"] = f"{{{', '.join(reversed(bitlist))}}}"

            # write data_in into single bits
            for bit in range(8):
                if (1 << bit) & self.inputs:
                    setup["data_in"].append(f"                                {self.name}_in{bit} <= data_in[{bit}];")

            for bit in range(8):
                if (1 << bit) & self.inputs:
                    self.INTERFACE[f"{self.name}_in{bit}"] = {
                        "size": 1,
                        "direction": "input",
                    }
                    self.SIGNALS[f"{self.name}_in{bit}"] = {
                        "direction": "input",
                        "bool": True,
                    }

                if (1 << bit) & self.outputs:
                    self.INTERFACE[f"{self.name}_out{bit}"] = {
                        "size": 1,
                        "direction": "output",
                    }
                    self.SIGNALS[f"{self.name}_out{bit}"] = {
                        "direction": "output",
                        "bool": True,
                    }
        else:
            self.INTERFACE[f"{self.name}_in"] = {
                "size": 8,
                "direction": "input",
            }
            self.INTERFACE[f"{self.name}_out"] = {
                "size": 8,
                "direction": "output",
            }
            self.SIGNALS[f"{self.name}_in"] = {
                "direction": "input",
                "min": 0,
                "max": 255,
            }
            self.SIGNALS[f"{self.name}_out"] = {
                "direction": "output",
                "min": 0,
                "max": 255,
            }
        self.INTERFACE[f"{self.name}_valid"] = {
            "size": 1,
            "direction": "input",
        }
        self.SIGNALS[f"{self.name}_valid"] = {
            "direction": "input",
            "bool": True,
        }

        self.PARAMS = {}
        self.INITS = []
        self.STEPS = [
            {
                "mode": "write",
                "var": f"{self.name}_out",
                "bytes": 1,
            },
        ]

        if self.inputs:
            self.STEPS.append(
                {
                    "mode": "read",
                    "var": f"{self.name}_in",
                    "bytes": 1,
                }
            )
