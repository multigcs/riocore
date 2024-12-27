class i2c_device:
    MEASURMENT_REG = "8'hF4"
    TEMPERATURE_CTRL = "8'h2E"
    READ_ADC_MSB_REG = "8'hF6"

    BMP180_CAL_AC1_REG = 0xAA  # ac1 pressure    computation
    BMP180_CAL_AC2_REG = 0xAC  # ac2 pressure    computation
    BMP180_CAL_AC3_REG = 0xAE  # ac3 pressure    computation
    BMP180_CAL_AC4_REG = 0xB0  # ac4 pressure    computation
    BMP180_CAL_AC5_REG = 0xB2  # ac5 temperature computation
    BMP180_CAL_AC6_REG = 0xB4  # ac6 temperature computation
    BMP180_CAL_B1_REG = 0xB6  # b1  pressure    computation
    BMP180_CAL_B2_REG = 0xB8  # b2  pressure    computation
    BMP180_CAL_MB_REG = 0xBA  # mb
    BMP180_CAL_MC_REG = 0xBC  # mc  temperature computation
    BMP180_CAL_MD_REG = 0xBE  # md  temperature computation

    options = {
        "addresses": ["0x77"],
    }

    def __init__(self, setup, system_setup={}):
        self.system_setup = system_setup
        self.name = setup["name"]
        self.addr = setup["address"]
        self.INTERFACE = {
            f"{self.name}_temp": {
                "size": 16,
                "direction": "input",
            },
            f"{self.name}_valid": {
                "size": 1,
                "direction": "input",
            },
        }
        self.SIGNALS = {
            f"{self.name}_temp": {
                "direction": "input",
                "format": "0.2f",
                "unit": "°C",
            },
            f"{self.name}_valid": {
                "direction": "input",
                "bool": True,
            },
        }
        self.PARAMS = {}
        self.INITS = []
        self.STEPS = [
            {
                "mode": "write",
                "value": f"{{{self.MEASURMENT_REG}, {self.TEMPERATURE_CTRL}}}",
                "bytes": 2,
            },
            {
                "mode": "write",
                "value": self.READ_ADC_MSB_REG,
                "bytes": 1,
            },
            {
                "mode": "read",
                "var": f"{self.name}_temp",
                "bytes": 2,
            },
        ]

    def convert(self, signal_name, signal_setup, value):
        if signal_name.endswith("_valid"):
            return value
        if signal_name.endswith("_temp"):
            return value / 1000.0
            """

            bmpAC5 = 25071
            bmpAC6 = 21139
            bmpMC = 53750
            bmpMD = 2777

            X1 = int(((value - bmpAC6) * bmpAC5) >> 15)
            X2 = int((bmpMC << 11) / (X1 + bmpMD))

            value = X1 + X2;
            """

            return value
        return value

    def convert_c(self, signal_name, signal_setup):
        if signal_name.endswith("_valid"):
            return ""
        return """
        value = value / 1000.0;
        """
