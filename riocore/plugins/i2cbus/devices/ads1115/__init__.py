class i2c_device:
    options = {
        "info": "16bit / 4channel adc",
        "description": "",
        "addresses": ["0x48", "0x49"],
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

    def __init__(self, setup, system_setup={}):
        self.system_setup = system_setup
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
                "unit": "V",
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

        self.INITS = []
        self.STEPS = []

        for channel in range(self.channels):
            setupRegister[2] = f"3'd{4 + channel}"
            self.STEPS += [
                {
                    "comment": "start conversion",
                    "mode": "write",
                    "value": f"{{{', '.join(setupRegister)}}}",
                    "bytes": 3,
                },
                {
                    "comment": "set status register",
                    "mode": "write",
                    "value": "8'd1",
                    "bytes": 1,
                },
                {
                    "comment": "check status",
                    "mode": "read",
                    "until": "data_in[7] == 1",
                    "timeout": 130,
                    "bytes": 1,
                },
                {
                    "comment": "set adc register",
                    "mode": "write",
                    "value": "8'd0",
                    "bytes": 1,
                },
                {
                    "comment": "read 16bit adc value",
                    "mode": "read",
                    "var": f"{self.name}_adc{channel}",
                    "bytes": 2,
                },
            ]

    def convert(self, signal_name, signal_setup, value):
        if signal_name.endswith("_valid"):
            return value
        # 3.3V range
        value = value >> 3
        value /= 1000.0
        return value
