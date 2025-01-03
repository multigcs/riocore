def signed(n, byte_count):
    return int.from_bytes(n.to_bytes(byte_count, "little", signed=False), "little", signed=True)


class i2c_device:
    options = {
        "info": "pressure and temperature sensor",
        "description": "",
        "addresses": ["0x76"],
    }

    BMP280_REGISTER_DIG_T1 = 0x88
    BMP280_REGISTER_DIG_T2 = 0x8A
    BMP280_REGISTER_DIG_T3 = 0x8C
    BMP280_REGISTER_DIG_P1 = 0x8E
    BMP280_REGISTER_DIG_P2 = 0x90
    BMP280_REGISTER_DIG_P3 = 0x92
    BMP280_REGISTER_DIG_P4 = 0x94
    BMP280_REGISTER_DIG_P5 = 0x96
    BMP280_REGISTER_DIG_P6 = 0x98
    BMP280_REGISTER_DIG_P7 = 0x9A
    BMP280_REGISTER_DIG_P8 = 0x9C
    BMP280_REGISTER_DIG_P9 = 0x9E
    BMP280_REGISTER_CHIPID = 0xD0
    BMP280_REGISTER_VERSION = 0xD1
    BMP280_REGISTER_SOFTRESET = 0xE0
    BMP280_REGISTER_CAL26 = 0xE1
    BMP280_REGISTER_STATUS = 0xF3
    BMP280_REGISTER_CONTROL = 0xF4
    BMP280_REGISTER_CONFIG = 0xF5
    BMP280_REGISTER_PRESSUREDATA = 0xF7
    BMP280_REGISTER_TEMPDATA = 0xFA

    def __init__(self, setup, system_setup={}):
        self.system_setup = system_setup
        self.name = setup["name"]
        self.addr = setup["address"]
        self.INTERFACE = {
            f"{self.name}_rawp": {
                "size": 32,
                "direction": "input",
                "multiplexed": True,
            },
            f"{self.name}_rawt": {
                "size": 32,
                "direction": "input",
                "multiplexed": True,
            },
            f"{self.name}_valid": {
                "size": 1,
                "direction": "input",
            },
        }
        self.SIGNALS = {
            f"{self.name}_rawp": {
                "direction": "input",
                "format": "0.1f",
                "unit": "hPa",
            },
            f"{self.name}_rawt": {
                "direction": "input",
                "format": "0.1f",
                "unit": "°C",
            },
            f"{self.name}_valid": {
                "direction": "input",
                "bool": True,
            },
        }

        init_regs = {
            "dig_T1": self.BMP280_REGISTER_DIG_T1,
            "dig_T2": self.BMP280_REGISTER_DIG_T2,
            "dig_T3": self.BMP280_REGISTER_DIG_T3,
            "dig_P1": self.BMP280_REGISTER_DIG_P1,
            "dig_P2": self.BMP280_REGISTER_DIG_P2,
            "dig_P3": self.BMP280_REGISTER_DIG_P3,
            "dig_P4": self.BMP280_REGISTER_DIG_P4,
            "dig_P5": self.BMP280_REGISTER_DIG_P5,
            "dig_P6": self.BMP280_REGISTER_DIG_P6,
            "dig_P7": self.BMP280_REGISTER_DIG_P7,
            "dig_P8": self.BMP280_REGISTER_DIG_P8,
            "dig_P9": self.BMP280_REGISTER_DIG_P9,
        }

        self.t_fine = 0
        self.PARAMS = {}
        self.DEFINES = []
        self.INITS = []

        for name, register in init_regs.items():
            self.INTERFACE[f"{self.name}_{name}"] = {
                "size": 32,
                "direction": "input",
                "multiplexed": True,
            }
            self.SIGNALS[f"{self.name}_{name}"] = {
                "direction": "input",
                "format": "d",
                "helper": True,
            }
            self.INITS.append(
                {
                    "mode": "readreg",
                    "register": register,
                    "var": f"{self.name}_{name}",
                    "big_endian": True,
                    "bytes": 2,
                }
            )

        self.STEPS = [
            {
                "mode": "write",
                "var": f"{{ 8'd{self.BMP280_REGISTER_CONTROL}, 8'd{0x25} }}",
                "bytes": 2,
            },
            {
                "mode": "delay",
                "ms": 8,
            },
            {
                "mode": "write",
                "var": f"8'd{self.BMP280_REGISTER_PRESSUREDATA}",
                "bytes": 1,
                "stop": False,
            },
            {
                "mode": "read",
                "data_in": [
                    "                                baro_rawp <= data_in[47:24];",
                    "                                baro_rawt <= data_in[23:0] ;",
                ],
                "bytes": 6,
                "stop": True,
            },
        ]

    def convert(self, signal_name, signal_setup, value):
        if signal_name.endswith("_valid"):
            return value

        if signal_name.endswith("_rawt"):
            name = signal_name.split("_")[0]
            dig_T1 = self.SIGNALS[f"{name}_dig_T1"]["value"]
            dig_T2 = signed(self.SIGNALS[f"{name}_dig_T2"]["value"], 2)
            dig_T3 = signed(self.SIGNALS[f"{name}_dig_T3"]["value"], 2)

            if dig_T1 and dig_T2 and dig_T3:
                adc_T = value / 16.0
                var1 = (adc_T / 16384.0 - dig_T1 / 1024.0) * dig_T2
                var2 = adc_T / 131072.0 - dig_T1 / 8192.0
                var2 = var2 * var2 * dig_T3
                self.t_fine = var1 + var2
                value = self.t_fine / 5120.0

        if signal_name.endswith("_rawp"):
            name = signal_name.split("_")[0]
            dig_P1 = self.SIGNALS[f"{name}_dig_P1"]["value"]
            dig_P2 = signed(self.SIGNALS[f"{name}_dig_P2"]["value"], 2)
            dig_P3 = signed(self.SIGNALS[f"{name}_dig_P3"]["value"], 2)
            dig_P4 = signed(self.SIGNALS[f"{name}_dig_P4"]["value"], 2)
            dig_P5 = signed(self.SIGNALS[f"{name}_dig_P5"]["value"], 2)
            dig_P6 = signed(self.SIGNALS[f"{name}_dig_P6"]["value"], 2)
            dig_P7 = signed(self.SIGNALS[f"{name}_dig_P7"]["value"], 2)
            dig_P8 = signed(self.SIGNALS[f"{name}_dig_P8"]["value"], 2)
            dig_P9 = signed(self.SIGNALS[f"{name}_dig_P9"]["value"], 2)

            if self.t_fine and dig_P1 and dig_P2 and dig_P3 and dig_P4 and dig_P5 and dig_P6 and dig_P7 and dig_P8 and dig_P9:
                adc_P = value / 16.0
                var1 = self.t_fine / 2.0 - 64000.0
                var2 = var1 * var1 * dig_P6 / 32768.0
                var2 = var2 + var1 * dig_P5 * 2
                var2 = var2 / 4.0 + dig_P4 * 65536.0
                var1 = (dig_P3 * var1 * var1 / 524288.0 + dig_P2 * var1) / 524288.0
                var1 = (1.0 + var1 / 32768.0) * dig_P1
                pressure = 1048576.0 - adc_P
                pressure = (pressure - var2 / 4096.0) * 6250.0 / var1
                var1 = dig_P9 * pressure * pressure / 2147483648.0
                var2 = pressure * dig_P8 / 32768.0
                value = (pressure + (var1 + var2 + dig_P7) / 16.0) / 100.0

        return value

    def convert_c(self, signal_name, signal_setup):
        if signal_name.endswith("_valid"):
            return ""
        return """
        value = value;
        """
