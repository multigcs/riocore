class i2c_device:
    def __init__(self, setup):
        self.name = setup["name"]
        self.addr = setup["address"]
        bitvar = setup.get("bitvar", False)
        self.INTERFACE = {}
        self.SIGNALS = {}
        if bitvar:
            setup["data_out"] = []
            setup["data_in"] = []

            # write single bots into data_out byte
            bitlist = []
            for bit in range(0, 8):
                bitlist.append(f"{self.name}_out{bit}")
            setup["data_out"].append(f"                            data_out <= {{{', '.join(reversed(bitlist))}}};")

            # write data_in into single bits
            for bit in range(0, 8):
                setup["data_in"].append(f"                                {self.name}_in{bit} <= data_in[{bit}];")

            for bit in range(0, 8):
                self.INTERFACE[f"{self.name}_in{bit}"] = {
                    "size": 1,
                    "direction": "input",
                }
                self.INTERFACE[f"{self.name}_out{bit}"] = {
                    "size": 1,
                    "direction": "output",
                }
                self.SIGNALS[f"{self.name}_in{bit}"] = {
                    "direction": "input",
                    "bool": True,
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
        self.PARAMS = {
            f"{self.name.upper()}_ADDR": self.addr,
        }

        self.INITS = []
        self.STEPS = [
            {
                "mode": "write",
                "var": f"{self.name}_out",
                "bytes": 1,
            },
            {
                "mode": "read",
                "var": f"{self.name}_in",
                "bytes": 1,
            },
        ]
