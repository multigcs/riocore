class i2c_device:
    options = {
        "addresses": ["0x48", "0x49", "0x4A", "0x4B"],
        "config": {
            "channels": {
                "type": int,
                "min": 1,
                "max": 4,
                "description": "number of channels",
                "default": 4,
            },
        },
    }

    def __init__(self, setup):
        self.name = setup["name"]
        self.addr = setup["address"]
        self.setup = setup
        self.channels = setup.get("channels", self.options["config"]["channels"]["default"])

        self.INTERFACE = {}
        self.SIGNALS = {}
        for channel in range(self.channels):
            self.INTERFACE[f"{self.name}_adc{channel}"] = {
                "size": 16,
                "direction": "input",
            }
            self.SIGNALS[f"{self.name}_adc{channel}"] = {
                "direction": "input",
                "format": "0.3f",
            }

        self.PARAMS = {}
        self.INITS = {}
        setupRegister = [
            "8'd1",  # Register-Address
            "1'b1",  # Start Conversion
            "3'b100",  # Channel 0 Single ended
            "3'b001",  # FSR +- 4.096v
            "1'b1",  # Single shot mode
            "3'b100",  # 128 SPS
            "1'b0",  # Traditional Comparator
            "1'b0",  # Active low alert
            "1'b0",  # Non latching
            "2'b11",  # Disable comparator
        ]

        registerAddr = ["8'd1"]

        self.INITS = []
        self.STEPS = []
        for channel in range(self.channels):
            setupRegister[1] = f"3'd{4 + channel}"
            self.STEPS += [
                {
                    # start conversion
                    "mode": "write",
                    "value": f"{{{', '.join(setupRegister)}}}",
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
                    "var": f"{self.name}_adc{channel}",
                    "var_set": "data_in[15] ? 12'd0 : data_in[14:3]",
                    "bytes": 2,
                },
            ]

    def convert(self, signal_name, signal_setup, value):
        value /= 1000.0
        return value
