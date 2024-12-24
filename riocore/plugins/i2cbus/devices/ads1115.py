class i2c_device:
    def __init__(self, setup):
        self.name = setup["name"]
        self.addr = setup["address"]
        self.setup = setup
        self.addresses = ["8'10010000", "8'b10010010", "8'b10010100", "8'b10010110"]
        self.INTERFACE = {
            f"{self.name}_adc0": {
                "size": 16,
                "direction": "input",
            },
            f"{self.name}_adc1": {
                "size": 16,
                "direction": "input",
            },
            f"{self.name}_adc2": {
                "size": 16,
                "direction": "input",
            },
            f"{self.name}_adc3": {
                "size": 16,
                "direction": "input",
            },
        }
        self.SIGNALS = {
            f"{self.name}_adc0": {
                "direction": "input",
                "format": "0.3f",
            },
            f"{self.name}_adc1": {
                "direction": "input",
                "format": "0.3f",
            },
            f"{self.name}_adc2": {
                "direction": "input",
                "format": "0.3f",
            },
            f"{self.name}_adc3": {
                "direction": "input",
                "format": "0.3f",
            },
        }
        self.PARAMS = {
            f"{self.name.upper()}_ADDR": self.addr,
        }

        self.INITS = {}
        setupRegister = [
            "1'b1",   # Start Conversion
            "3'b100", # Channel 0 Single ended
            "3'b001", # FSR +- 4.096v
            "1'b1",   # Single shot mode
            "3'b100", # 128 SPS
            "1'b0",   # Traditional Comparator
            "1'b0",   # Active low alert
            "1'b0",   # Non latching
            "2'b11",  # Disable comparator
        ]
        
        registerAddr = ["8'd1"]

        self.INITS = []
        self.STEPS = []
        for adc_n in range(4):
            setupRegister[1] = f"3'd{4 + adc_n}"
            self.STEPS += [
                {
                    # start conversion
                    "mode": "write",
                    "value": f"{{{', '.join(registerAddr + setupRegister)}}}",
                    "bytes": 3,
                },
                {
                    # write next register id
                    "mode": "write",
                    "value": f"{{{', '.join(registerAddr)}}}",
                    "bytes": 1,
                    "until": "",
                },
                {
                    # check status
                    "mode": "read",
                    "until": "data_in[7] == 1",
                    "bytes": 1,
                },
                {
                    "mode": "write",
                    "value": "8'd0",
                    "bytes": 1,
                },
                {
                    "mode": "read",
                    "var": f"{self.name}_adc{adc_n}",
                    "var_set": "data_in[15] ? 12'd0 : data_in[14:3]",
                    "bytes": 2,
                },
            ]


    def convert(self, signal_name, signal_setup, value):
        channel = signal_name[-1]
        value /= 1000.0
        return value
