class i2c_device:
    options = {
        "info": "ToF Distance Sensor",
        "description": "Time-of-Flight ToF Laser Ranging Distance Sensor 940nm",
        "addresses": ["0x29"],
    }

    def __init__(self, setup, system_setup={}):
        self.system_setup = system_setup
        self.name = setup["name"]
        self.addr = setup["address"]
        self.INTERFACE = {
            f"{self.name}_distance": {
                "size": 16,
                "direction": "input",
                "multiplexed": True,
            },
            f"{self.name}_error": {
                "size": 1,
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
            f"{self.name}_distance": {
                "direction": "input",
                "format": "d",
                "unit": "mm",
            },
            f"{self.name}_error": {
                "direction": "input",
                "bool": True,
                "unit": "",
            },
            f"{self.name}_valid": {
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
                "mode": "write",
                "value": f"{VL53L0X_REG_RESULT_RANGE_STATUS + 10}",
                "bytes": 1,
            },
            {
                "mode": "read",
                "var": f"{self.name}_distance",
                "bytes": 2,
            },
            {
                "mode": "write",
                "value": f"{VL53L0X_REG_RESULT_RANGE_STATUS}",
                "bytes": 1,
            },
            {
                "mode": "read",
                "data_in": [f"                                {self.name}_error <= ~data_in[4];"],
                "bytes": 1,
            },
        ]
        self.last_valid = 0
        self.last_value = 0

    def convert(self, signal_name, signal_setup, value):
        if signal_name.endswith("_valid"):
            return value
        elif signal_name.endswith("_error"):
            return value
        self.last_value = value
        if value > 20:
            self.last_valid = value
        else:
            value = self.last_valid
        return value

    def convert_c(self, signal_name, signal_setup):
        if signal_name.endswith("_valid"):
            return ""
        elif signal_name.endswith("_error"):
            return ""
        return """
        value = value;
        """
