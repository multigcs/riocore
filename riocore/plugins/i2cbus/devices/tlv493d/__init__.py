class i2c_device:
    options = {
        "info": "3axis magnetic sensor",
        "description": "",
        "addresses": ["0x5E", "0x1F"],
    }

    def __init__(self, setup, system_setup={}):
        self.system_setup = system_setup
        self.name = setup["name"]
        self.addr = setup["address"]
        self.INTERFACE = {
            f"{self.name}_x": {
                "size": 16,
                "direction": "input",
                "multiplexed": True,
            },
            f"{self.name}_y": {
                "size": 16,
                "direction": "input",
                "multiplexed": True,
            },
            f"{self.name}_z": {
                "size": 16,
                "direction": "input",
                "multiplexed": True,
            },
            f"{self.name}_valid": {
                "size": 1,
                "direction": "input",
                "multiplexed": True,
            },
        }
        self.SIGNALS = {
            f"{self.name}_x": {
                "direction": "input",
                "format": "0.1f",
                "unit": "",
            },
            f"{self.name}_y": {
                "direction": "input",
                "format": "0.1f",
                "unit": "",
            },
            f"{self.name}_z": {
                "direction": "input",
                "format": "0.1f",
                "unit": "",
            },
            f"{self.name}_valid": {
                "direction": "input",
                "bool": True,
            },
        }
        self.PARAMS = {}
        self.INITS = [
            {
                "mode": "writereg",
                "values": [
                    (0x11, 0x01),
                ],
            },
        ]
        self.STEPS = [
            {
                "mode": "write",
                "value": 0x00,
                "bytes": 1,
            },
            {
                "mode": "read",
                "data_in": [
                    f"{self.name}_x <= {{ 4'd0, data_in[47:40], data_in[19:16] }};\n",
                    f"{self.name}_y <= {{ 4'd0, data_in[39:32], data_in[11:8] }};\n",
                    f"{self.name}_z <= {{ 4'd0, data_in[31:24], data_in[3:0] }};\n",
                ],
                "bytes": 6,
            },
        ]

        self.offsets_cnt = 10
        self.offsets = {}

    def convert(self, signal_name, signal_setup, value):
        if signal_name.endswith("_valid"):
            return value

        if value > 2047:
            value = value - 4096

        if self.offsets_cnt > 0:
            self.offsets_cnt -= 1
        else:
            if signal_name not in self.offsets:
                self.offsets[signal_name] = value
                print("", signal_name, value)
            else:
                value -= self.offsets[signal_name]

        return value

    def convert_c(self, signal_name, signal_setup):
        if signal_name.endswith("_valid"):
            return ""
        return """
        value = value;
        """
