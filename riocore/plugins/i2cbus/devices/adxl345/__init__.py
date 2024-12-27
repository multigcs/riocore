import math


class i2c_device:
    options = {
        "addresses": ["0x53"],
        "config": {
            "units": {
                "type": "combo",
                "options": ["deg", "gforce", "raw"],
                "description": "unit of the data",
                "default": "gforce",
            },
            "offset_x": {
                "type": float,
                "min": -2.0,
                "max": 2.0,
                "description": "offset for the x axis (g-force)",
                "default": 0,
            },
            "offset_y": {
                "type": float,
                "min": -2.0,
                "max": 2.0,
                "description": "offset for the x axis (g-force)",
                "default": 0,
            },
            "offset_z": {
                "type": float,
                "min": -2.0,
                "max": 2.0,
                "description": "offset for the x axis (g-force)",
                "default": 0,
            },
        },
    }

    # registers
    ADXL345_DEVID = 0x00
    ADXL345_THRESH_TAP = 0x1D
    ADXL345_OFSX = 0x1E
    ADXL345_OFSY = 0x1F
    ADXL345_OFSZ = 0x20
    ADXL345_DUR = 0x21
    ADXL345_LATENT = 0x22
    ADXL345_WINDOW = 0x23
    ADXL345_THRESH_ACT = 0x24
    ADXL345_THRESH_INACT = 0x25
    ADXL345_TIME_INACT = 0x26
    ADXL345_ACT_INACT_CTL = 0x27
    ADXL345_THRESH_FF = 0x28
    ADXL345_TIME_FF = 0x29
    ADXL345_TAP_AXES = 0x2A
    ADXL345_ACT_TAP_STATUS = 0x2B
    ADXL345_BW_RATE = 0x2C
    ADXL345_POWER_CTL = 0x2D
    ADXL345_INT_ENABLE = 0x2E
    ADXL345_INT_MAP = 0x2F
    ADXL345_INT_SOURCE = 0x30
    ADXL345_DATA_FORMAT = 0x31
    ADXL345_DATAX0 = 0x32
    ADXL345_DATAX1 = 0x33
    ADXL345_DATAY0 = 0x34
    ADXL345_DATAY1 = 0x35
    ADXL345_DATAZ0 = 0x36
    ADXL345_DATAZ1 = 0x37
    ADXL345_FIFO_CTL = 0x38
    ADXL345_FIFO_STATUS = 0x39

    # Register bits
    ADXL345_FULL_RES = 0x03
    ADXL345_SUPPRESS = 0x03
    ADXL345_LOW_POWER = 0x04
    ADXL345_MEASURE = 0x03

    # Other
    MILLI_G_PER_LSB = 3.9
    UNITS_PER_G = 256.41

    def __init__(self, setup, system_setup={}):
        self.system_setup = system_setup
        self.name = setup["name"]
        self.addr = setup["address"]
        self.units = setup.get("units", self.options["config"]["units"]["default"])
        self.offset_x = setup.get("offset_x", self.options["config"]["offset_x"]["default"])
        self.offset_y = setup.get("offset_y", self.options["config"]["offset_y"]["default"])
        self.offset_z = setup.get("offset_z", self.options["config"]["offset_z"]["default"])
        self.INTERFACE = {
            f"{self.name}_x": {
                "size": 16,
                "signed": True,
                "direction": "input",
            },
            f"{self.name}_y": {
                "size": 16,
                "signed": True,
                "direction": "input",
            },
            f"{self.name}_z": {
                "size": 16,
                "signed": True,
                "direction": "input",
            },
            f"{self.name}_valid": {
                "size": 1,
                "direction": "input",
            },
        }
        self.SIGNALS = {
            f"{self.name}_x": {
                "direction": "input",
                "format": "0.3f",
                "offset": self.offset_x,
                "units": self.units,
            },
            f"{self.name}_y": {
                "direction": "input",
                "format": "0.3f",
                "offset": self.offset_y,
                "units": self.units,
            },
            f"{self.name}_z": {
                "direction": "input",
                "format": "0.3f",
                "offset": self.offset_z,
                "units": self.units,
            },
            f"{self.name}_valid": {
                "direction": "input",
                "bool": True,
            },
        }
        if self.units == "deg":
            self.SIGNALS[f"{self.name}_x"]["unit"] = "°"
            self.SIGNALS[f"{self.name}_y"]["unit"] = "°"
            self.SIGNALS[f"{self.name}_z"]["unit"] = "g"
        elif self.units == "gforce":
            self.SIGNALS[f"{self.name}_x"]["unit"] = "g"
            self.SIGNALS[f"{self.name}_y"]["unit"] = "g"
            self.SIGNALS[f"{self.name}_z"]["unit"] = "g"

        self.PARAMS = {}
        self.INITS = [
            {
                "mode": "writereg",
                "values": [
                    (self.ADXL345_POWER_CTL, 0),
                    (self.ADXL345_POWER_CTL, 16),
                    (self.ADXL345_POWER_CTL, 16 | (1 << self.ADXL345_MEASURE)),
                    (self.ADXL345_DATA_FORMAT, (1 << self.ADXL345_FULL_RES)),
                    (self.ADXL345_INT_ENABLE, 0),
                    (self.ADXL345_INT_MAP, 0),
                    (self.ADXL345_TIME_INACT, 0),
                    (self.ADXL345_THRESH_INACT, 0),
                    (self.ADXL345_ACT_INACT_CTL, 0),
                    (self.ADXL345_DUR, 0),
                    (self.ADXL345_LATENT, 0),
                    (self.ADXL345_THRESH_TAP, 0),
                    (self.ADXL345_TAP_AXES, 0),
                    (self.ADXL345_WINDOW, 0),
                    (self.ADXL345_FIFO_CTL, 0),
                    (self.ADXL345_FIFO_STATUS, 0),
                ],
            },
        ]
        self.STEPS = [
            {
                "mode": "readreg",
                "register": self.ADXL345_DATAX0,
                "var": f"{self.name}_x",
                "big_endian": True,
                "bytes": 2,
            },
            {
                "mode": "readreg",
                "register": self.ADXL345_DATAY0,
                "var": f"{self.name}_y",
                "big_endian": True,
                "bytes": 2,
            },
            {
                "mode": "readreg",
                "register": self.ADXL345_DATAZ0,
                "var": f"{self.name}_z",
                "big_endian": True,
                "bytes": 2,
            },
        ]

    def convert(self, signal_name, signal_setup, value):
        if signal_name.endswith("_valid"):
            return value
        units = signal_setup["units"]
        # unsigned -> signed
        if value > 32767:
            value = value - 65535

        if units != "raw":
            value = value * self.MILLI_G_PER_LSB / 1000
            value -= signal_setup.get("offset", 0.0)

        if units == "deg" and not signal_name.endswith("_z"):
            if value > 1:
                value = 1
            if value < -1:
                value = -1
            value = math.asin(value) * 57.296

        return value

    def convert_c(self, signal_name, signal_setup):
        if signal_name.endswith("_valid"):
            return ""
        return """
        value = value
        """
