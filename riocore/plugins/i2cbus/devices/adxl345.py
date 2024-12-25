class i2c_device:
    options = {
        "addresses": ["0x53"],
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

    def __init__(self, setup):
        self.name = setup["name"]
        self.addr = setup["address"]
        self.INTERFACE = {
            f"{self.name}_x": {
                "size": 16,
                "direction": "input",
            },
            f"{self.name}_y": {
                "size": 16,
                "direction": "input",
            },
            f"{self.name}_z": {
                "size": 16,
                "direction": "input",
            },
        }
        self.SIGNALS = {
            f"{self.name}_x": {
                "direction": "input",
                "format": "0.1f",
            },
            f"{self.name}_y": {
                "direction": "input",
                "format": "0.1f",
            },
            f"{self.name}_z": {
                "direction": "input",
                "format": "0.1f",
            },
        }
        self.PARAMS = {}
        self.INITS = [
            {
                "mode": "write",
                "value": f"{{8'd{self.ADXL345_POWER_CTL}, 8'd{0}}}",
                "bytes": 2,
            },
            {
                "mode": "write",
                "value": f"{{8'd{self.ADXL345_POWER_CTL}, 8'd{16}}}",
                "bytes": 2,
            },
            {
                "mode": "write",
                "value": f"{{8'd{self.ADXL345_POWER_CTL}, 8'd{16 | (1<<self.ADXL345_MEASURE)}}}",
                "bytes": 2,
            },
            {
                "mode": "write",
                "value": f"{{8'd{self.ADXL345_DATA_FORMAT}, 8'd{(1<<self.ADXL345_FULL_RES)}}}",
                "bytes": 2,
            },
            {
                "mode": "write",
                "value": f"{{8'd{self.ADXL345_INT_ENABLE}, 8'd{0}}}",
                "bytes": 2,
            },
            {
                "mode": "write",
                "value": f"{{8'd{self.ADXL345_INT_MAP}, 8'd{0}}}",
                "bytes": 2,
            },
            {
                "mode": "write",
                "value": f"{{8'd{self.ADXL345_TIME_INACT}, 8'd{0}}}",
                "bytes": 2,
            },
            {
                "mode": "write",
                "value": f"{{8'd{self.ADXL345_THRESH_INACT}, 8'd{0}}}",
                "bytes": 2,
            },
            {
                "mode": "write",
                "value": f"{{8'd{self.ADXL345_ACT_INACT_CTL}, 8'd{0}}}",
                "bytes": 2,
            },
            {
                "mode": "write",
                "value": f"{{8'd{self.ADXL345_DUR}, 8'd{0}}}",
                "bytes": 2,
            },
            {
                "mode": "write",
                "value": f"{{8'd{self.ADXL345_LATENT}, 8'd{0}}}",
                "bytes": 2,
            },
            {
                "mode": "write",
                "value": f"{{8'd{self.ADXL345_THRESH_TAP}, 8'd{0}}}",
                "bytes": 2,
            },
            {
                "mode": "write",
                "value": f"{{8'd{self.ADXL345_TAP_AXES}, 8'd{0}}}",
                "bytes": 2,
            },
            {
                "mode": "write",
                "value": f"{{8'd{self.ADXL345_WINDOW}, 8'd{0}}}",
                "bytes": 2,
            },
            {
                "mode": "write",
                "value": f"{{8'd{self.ADXL345_FIFO_CTL}, 8'd{0}}}",
                "bytes": 2,
            },
            {
                "mode": "write",
                "value": f"{{8'd{self.ADXL345_FIFO_STATUS}, 8'd{0}}}",
                "bytes": 2,
            },
        ]
        self.STEPS = [
            {
                "mode": "write",
                "value": f"{self.ADXL345_DATAX0}",
                "bytes": 1,
            },
            {
                "mode": "read",
                "var": f"{self.name}_x",
                "bytes": 2,
            },
            {
                "mode": "write",
                "value": f"{self.ADXL345_DATAY0}",
                "bytes": 1,
            },
            {
                "mode": "read",
                "var": f"{self.name}_y",
                "bytes": 2,
            },
            {
                "mode": "write",
                "value": f"{self.ADXL345_DATAZ0}",
                "bytes": 1,
            },
            {
                "mode": "read",
                "var": f"{self.name}_z",
                "bytes": 2,
            },
        ]

    def convert(self, signal_name, signal_setup, value):
        return value

    def convert_c(self, signal_name, signal_setup):
        return """
        value = value
        """
