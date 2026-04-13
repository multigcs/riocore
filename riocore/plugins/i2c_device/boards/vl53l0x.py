class i2c_device:
    options = {
        "info": "ToF Distance Sensor",
        "description": "Time-of-Flight ToF Laser Ranging Distance Sensor 940nm",
        "addresses": ["0x29"],
    }

    def __init__(self, parent, system_setup=None):
        self.system_setup = system_setup or {}
        self.name = parent.instances_name
        self.INTERFACE = {
            "distance": {
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
            "distance": {
                "direction": "input",
                "format": "0.1f",
                "unit": "mm",
            },
            "valid": {
                "direction": "input",
                "bool": True,
            },
        }
        self.PARAMS = {}

        VL53L0X_REG_SYSRANGE_START = 0x00
        VL53L0X_REG_SYSRANGE_MODE_BACKTOBACK = 0x02
        VL53L0X_REG_RESULT_RANGE_STATUS = 0x14

        self.INITS = [
            {
                "mode": "writereg",
                "values": [
                    (0x80, 0x01),
                    (0xFF, 0x01),
                    (0x00, 0x00),
                    (0x91, 0x3C),
                    (0x00, 0x01),
                    (0xFF, 0x00),
                    (0x80, 0x00),
                    (VL53L0X_REG_SYSRANGE_START, VL53L0X_REG_SYSRANGE_MODE_BACKTOBACK),
                ],
            },
        ]
        self.STEPS = [
            {
                "comment": "check status",
                "mode": "readreg",
                "register": VL53L0X_REG_RESULT_RANGE_STATUS,
                "until": "data_in[4] == 1",
                "timeout": 100,
                "bytes": 1,
            },
            {
                "mode": "write",
                "value": f"{VL53L0X_REG_RESULT_RANGE_STATUS + 10}",
                "bytes": 1,
            },
            {
                "mode": "read",
                "var": f"{self.name}_distance",
                "bytes": 2,
            },
        ]
        self.last_valid = 0
        self.last_value = 0
        self.PINDEFAULTS = {
            "I2C": {"direction": "output", "edge": "target", "pos": [20, 30], "type": ["I2C"], "bus": True},
            "I2C:OUT": {"direction": "output", "edge": "source", "pos": [36, 30], "type": ["PASSTHROUGH"], "bus": True, "pintype": "PASSTHROUGH", "source": "I2C"},
        }

    def convert_c(self, signal_name, signal_setup):
        if signal_name == "valid":
            return ""
        return """
        value = value;
        """
