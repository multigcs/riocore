class i2c_device:
    options = {
        "info": "3axis magnetic sensor",
        "description": "",
        "addresses": ["0x5E", "0x1F"],
    }

    def __init__(self, parent, system_setup=None):
        self.system_setup = system_setup or {}
        self.name = parent.instances_name
        self.INTERFACE = {
            "x": {
                "size": 16,
                "direction": "input",
                "multiplexed": True,
            },
            "y": {
                "size": 16,
                "direction": "input",
                "multiplexed": True,
            },
            "z": {
                "size": 16,
                "direction": "input",
                "multiplexed": True,
            },
            "valid": {
                "size": 1,
                "direction": "input",
                "multiplexed": True,
            },
        }
        self.SIGNALS = {
            "x": {
                "direction": "input",
                "format": "0.1f",
                "unit": "",
            },
            "y": {
                "direction": "input",
                "format": "0.1f",
                "unit": "",
            },
            "z": {
                "direction": "input",
                "format": "0.1f",
                "unit": "",
            },
            "valid": {
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
        self.PINDEFAULTS = {
            "I2C": {"direction": "output", "edge": "target", "pos": [50, 70], "type": ["I2C"], "bus": True},
            "I2C:OUT": {"direction": "output", "edge": "source", "pos": [70, 70], "type": ["PASSTHROUGH"], "bus": True, "pintype": "PASSTHROUGH", "source": "I2C"},
        }

    def convert_c(self, signal_name, signal_setup):
        if signal_name == "valid":
            return ""
        return """
        value = value;
        """
