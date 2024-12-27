class i2c_device:
    options = {
        "info": "16 channel pwm output",
        "description": "",
        "addresses": ["0x40"],
        "config": {
            "frequency": {
                "type": int,
                "description": "frequency",
                "min": 10,
                "max": 2000,
                "default": 100,
            },
            "channels": {
                "type": int,
                "min": 1,
                "max": 16,
                "description": "number of channels",
                "default": 16,
            },
            "units": {
                "type": "combo",
                "options": ["ms", "%", "rc %", "rc arc"],
                "description": "unit of the control unit",
                "default": "%",
            },
        },
    }

    PCA9685_MODE1 = 0x00
    PCA9685_MODE2 = 0x01
    PCA9685_MIN_FREQ = 24
    PCA9685_MAX_FREQ = 1526
    PCA9685_MODE1_RESTART = 0x80  #  0 = disable      1 = enable
    PCA9685_MODE1_EXTCLK = 0x40  #  0 = internal     1 = external (datasheet)
    PCA9685_MODE1_AUTOINCR = 0x20  #  0 = disable      1 = enable
    PCA9685_MODE1_SLEEP = 0x10  #  0 = normal       1 = sleep
    PCA9685_MODE1_SUB1 = 0x08  #  0 = disable      1 = enable
    PCA9685_MODE1_SUB2 = 0x04  #  0 = disable      1 = enable
    PCA9685_MODE1_SUB3 = 0x02  #  0 = disable      1 = enable
    PCA9685_MODE1_ALLCALL = 0x01  #  0 = disable      1 = enable
    PCA9685_MODE1_NONE = 0x00
    PCA9685_MODE2_INVERT = 0x10  #  0 = normal       1 = inverted
    PCA9685_MODE2_ACK = 0x08  #  0 = on STOP      1 = on ACK
    PCA9685_MODE2_TOTEMPOLE = 0x04  #  0 = open drain   1 = totem-pole
    PCA9685_MODE2_OUTNE = 0x03  #  datasheet
    PCA9685_MODE2_NONE = 0x00
    PCA9685_PRE_SCALER = 0xFE
    PCA9685_CHANNEL_0 = 0x06

    def __init__(self, setup, system_setup={}):
        self.system_setup = system_setup
        self.name = setup["name"]
        self.addr = setup["address"]
        self.frequency = setup.get("frequency", self.options["config"]["frequency"]["default"])
        self.units = setup.get("units", self.options["config"]["units"]["default"])
        self.channels = setup.get("channels", self.options["config"]["channels"]["default"])
        self.INTERFACE = {}
        self.SIGNALS = {}
        for channel in range(self.channels):
            self.INTERFACE[f"{self.name}_ch{channel}"] = {
                "size": 16,
                "direction": "output",
                "multiplexed": True,
            }
            if self.units == "ms":
                self.SIGNALS[f"{self.name}_ch{channel}"] = {
                    "direction": "output",
                    "min": 0,
                    "max": 1 * 1000 // self.frequency,
                    "unit": "ms",
                }
            elif self.units == "rc %":
                self.SIGNALS[f"{self.name}_ch{channel}"] = {
                    "direction": "output",
                    "min": 0,
                    "max": 100,
                    "unit": "%",
                }
            elif self.units == "rc arc":
                self.SIGNALS[f"{self.name}_ch{channel}"] = {
                    "direction": "output",
                    "min": 0,
                    "max": 180,
                    "unit": "degrees",
                }
            else:
                self.SIGNALS[f"{self.name}_ch{channel}"] = {
                    "direction": "output",
                    "min": 0,
                    "max": 100,
                    "unit": "%",
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
                "value": f"{{8'd{self.PCA9685_MODE1_AUTOINCR}, 8'd{(0x01)}}}",  # autoincr
                "bytes": 2,
            },
            {
                "mode": "write",
                "value": f"{{8'd{self.PCA9685_MODE2}, 8'd{(0x04)}}}",  # mode2 + sleep
                "bytes": 2,
            },
            {
                "mode": "write",
                "value": f"{{8'd{self.PCA9685_MODE1}, 8'd{0x01}}}",  # mode1
                "bytes": 2,
            },
            {
                "mode": "delay",
                "ms": 5,  # 5ms delay
            },
            {
                "mode": "write",
                "value": f"{{8'd{self.PCA9685_MODE1}, 8'd{(0x11)}}}",  # mode1 + sleep
                "bytes": 2,
            },
            {
                "mode": "write",
                "value": f"{{8'd{self.PCA9685_PRE_SCALER}, 8'd{int(25000000 / 4096.0 / self.frequency - 1)}}}",  # prescaler
                "bytes": 2,
            },
            {
                "mode": "write",
                "value": f"{{8'd{self.PCA9685_MODE1}, 8'd{(0x01)}}}",  # mode1 (unsleep)
                "bytes": 2,
            },
            {
                "mode": "delay",
                "ms": 5,  # 5ms delay
            },
            {
                "mode": "write",
                "value": f"{{8'd{self.PCA9685_MODE1}, 8'd{(0x01 | 0x80)}}}",  # mode1 (unsleep)
                "bytes": 2,
            },
            {
                "mode": "write",
                "value": f"{{8'd{0xFA}, 16'd{0}}}",  # pulse len
                "bytes": 3,
            },
        ]
        self.STEPS = [
            {
                "mode": "write",
                "value": f"{{8'd{self.PCA9685_MODE1}, 8'd{(0x01 | 0x80)}}}",  # mode1 (unsleep)
                "bytes": 2,
            },
            {
                "mode": "write",
                "value": f"{{8'd{0xFA}, 16'd{0}}}",  # pulse len
                "bytes": 3,
            },
        ]
        for channel in range(self.channels):
            self.STEPS.append(
                {
                    "mode": "write",
                    "value": f"{{8'd{self.PCA9685_CHANNEL_0 + channel * 4 + 2}, {self.name}_ch{channel}[7:0]}}",  # pulse len
                    "bytes": 2,
                }
            )
            self.STEPS.append(
                {
                    "mode": "write",
                    "value": f"{{8'd{self.PCA9685_CHANNEL_0 + channel * 4 + 3}, {self.name}_ch{channel}[15:8]}}",  # pulse len
                    "bytes": 2,
                }
            )

    def convert(self, signal_name, signal_setup, value):
        if signal_name.endswith("_valid"):
            return value
        if self.units == "ms":
            value = self.frequency * 4095 * value // 1000
        elif self.units == "rc %":
            value = self.frequency * 4095 * (1 / 100 * value + 1.0) // 1000
        elif self.units == "rc arc":
            value = self.frequency * 4095 * (1 / 180 * value + 1.0) // 1000
        else:
            value = value * 4095 // 100
        return value

    def convert_c(self, signal_name, signal_setup):
        if signal_name.endswith("_valid"):
            return ""
        if self.units:
            return f"""
            value = {self.frequency} * 4095 * value / 1000;
            """
        elif self.units == "rc %":
            return """
            value = {self.frequency} * 4095 * (1 / 100 * value + 1.0) / 1000;
            """
        elif self.units == "rc arc":
            return """
            value = {self.frequency} * 4095 * (1 / 180 * value + 1.0) / 1000;
            """
        else:
            return """
            value = value * 4095 / 100;
            """
