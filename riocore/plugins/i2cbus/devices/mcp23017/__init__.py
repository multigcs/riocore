class i2c_device:
    options = {
        "info": "16bit io-expander",
        "description": "",
        "addresses": ["0x20", "0x21", "0x22", "0x23", "0x24", "0x25", "0x26", "0x27"],
        "config": {
            "expansion": {
                "type": bool,
                "description": "use as expansion io",
                "default": False,
            },
            "directions_a": {
                "type": "bits",
                "width": 8,
                "min": 0,
                "max": 255,
                "description": "use as input",
                "default": 0,
            },
            "pullups_a": {
                "type": "bits",
                "width": 8,
                "min": 0,
                "max": 255,
                "description": "activate pullup on inputs",
                "default": 0,
            },
            "inverts_a": {
                "type": "bits",
                "width": 8,
                "min": 0,
                "max": 255,
                "description": "invert pin signal",
                "default": 0,
            },
            "directions_b": {
                "type": "bits",
                "width": 8,
                "min": 0,
                "max": 255,
                "description": "use as input",
                "default": 0,
            },
            "pullups_b": {
                "type": "bits",
                "width": 8,
                "min": 0,
                "max": 255,
                "description": "activate pullup on inputs",
                "default": 0,
            },
            "inverts_b": {
                "type": "bits",
                "width": 8,
                "min": 0,
                "max": 255,
                "description": "invert pin signal",
                "default": 0,
            },
        },
    }

    def __init__(self, setup, system_setup={}):
        self.IODIR_A = 0x00
        self.IODIR_B = 0x01
        self.IPOL_A = 0x02
        self.IPOL_B = 0x03
        self.GPPU_A = 0x0C
        self.GPPU_B = 0x0D
        self.GPIO_A = 0x12
        self.GPIO_B = 0x13

        self.system_setup = system_setup
        self.name = setup["name"]
        self.addr = setup["address"]
        self.INTERFACE = {}
        self.SIGNALS = {}
        self.directions = {}
        self.inverts = {}
        self.pullups = {}
        bitlist_out = {}
        bitlist_in = {}
        directions = {}
        pullups = {}
        inverts = {}
        for bank in ("a", "b"):
            bitlist_out[bank] = []
            bitlist_in[bank] = []
            directions[bank] = []
            pullups[bank] = []
            inverts[bank] = []
            self.directions[bank] = setup.get(f"directions_{bank}", self.options["config"][f"directions_{bank}"]["default"])
            self.inverts[bank] = setup.get(f"inverts_{bank}", self.options["config"][f"inverts_{bank}"]["default"])
            self.pullups[bank] = setup.get(f"pullups_{bank}", self.options["config"][f"pullups_{bank}"]["default"])
            for bit in range(0, 8):
                if (1 << bit) & self.directions[bank]:
                    directions[bank].append("1'd0")
                    bitlist_out[bank].append(f"{self.name}_{bank}{bit}out")
                    bitlist_in[bank].append(None)
                else:
                    directions[bank].append("1'd1")
                    bitlist_out[bank].append("1'd0")
                    bitlist_in[bank].append(f"{self.name}_{bank}{bit}in")
                if (1 << bit) & self.pullups[bank]:
                    pullups[bank].append("1'd1")
                else:
                    pullups[bank].append("1'd0")

                if (1 << bit) & self.inverts[bank]:
                    inverts[bank].append("1'd1")
                else:
                    inverts[bank].append("1'd0")
            for bit in range(0, 8):
                if (1 << bit) & self.directions[bank]:
                    self.INTERFACE[f"{self.name}_{bank}{bit}out"] = {
                        "size": 1,
                        "direction": "output",
                    }
                    self.SIGNALS[f"{self.name}_{bank}{bit}out"] = {
                        "direction": "output",
                        "bool": True,
                    }
            for bit in range(0, 8):
                if not (1 << bit) & self.directions[bank]:
                    self.INTERFACE[f"{self.name}_{bank}{bit}in"] = {
                        "size": 1,
                        "direction": "input",
                    }
                    self.SIGNALS[f"{self.name}_{bank}{bit}in"] = {
                        "direction": "input",
                        "bool": True,
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
        self.INITS = [
            {
                "mode": "write",
                "value": f"{{ 8'd{0x0a}, 8'b00000000 }}",
                "bytes": 2,
            },
        ]
        self.STEPS = []
        for bank_n, bank in enumerate(("a", "b")):
            self.INITS += [
                {
                    "mode": "write",
                    "value": f"{{ 8'd{self.IODIR_A+bank_n}, {', '.join(reversed(directions[bank]))} }}",
                    "bytes": 2,
                },
                {
                    "mode": "write",
                    "value": f"{{ 8'd{self.GPPU_A+bank_n}, {', '.join(reversed(pullups[bank]))} }}",
                    "bytes": 2,
                },
                {
                    "mode": "write",
                    "value": f"{{ 8'd{self.IPOL_A+bank_n}, {', '.join(reversed(inverts[bank]))} }}",
                    "bytes": 2,
                },
            ]

            self.STEPS += [
                {
                    "mode": "write",
                    "value": f"{{ 8'd{self.GPIO_A+bank_n}, {', '.join(reversed(bitlist_out[bank]))} }}",
                    "bytes": 2,
                },
            ]

            if bitlist_in[bank]:
                bitlist = []
                for bit_n, var in enumerate(bitlist_in[bank]):
                    if var:
                        bitlist.append(f"                                {var} <= data_in[{bit_n}];")

                if bitlist:
                    self.STEPS.append(
                        {
                            "mode": "write",
                            "value": f"{{ 8'd{self.GPIO_A+bank_n} }}",
                            "bytes": 1,
                        }
                    )
                    self.STEPS.append(
                        {
                            "mode": "read",
                            "data_in": bitlist,
                            "bytes": 1,
                        }
                    )
