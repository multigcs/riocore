class i2c_device:
    options = {
        "info": "current sensor",
        "description": "Zero-Drift, Bidirectional Current/Power Monitor",
        "addresses": ["0x40", "0x41", "0x45", "0x46"],
        "config": {
            "current-range": {
                "type": "combo",
                "options": ["400mA", "800mA", "1600mA", "3200mA"],
                "description": "max current",
                "default": "3200mA",
            },
            "voltage-range": {
                "type": "combo",
                "options": ["16V", "32V"],
                "description": "max voltage",
                "default": "32V",
            },
        },
    }

    def __init__(self, setup, system_setup={}):
        self.system_setup = system_setup
        self.name = setup["name"]
        self.addr = setup["address"]
        self.INTERFACE = {
            f"{self.name}_current": {
                "size": 16,
                "direction": "input",
                "multiplexed": True,
            },
            f"{self.name}_voltage": {
                "size": 16,
                "direction": "input",
                "multiplexed": True,
            },
            f"{self.name}_valid": {
                "size": 1,
                "direction": "input",
            },
        }
        self.SIGNALS = {
            f"{self.name}_current": {
                "direction": "input",
                "format": "0.1f",
                "unit": "mA",
            },
            f"{self.name}_voltage": {
                "direction": "input",
                "format": "0.1f",
                "unit": "V",
            },
            f"{self.name}_valid": {
                "direction": "input",
                "bool": True,
            },
        }
        self.PARAMS = {}

        bits_pg = "11"
        crange = setup.get("current-range", "3200mA")
        if crange == "400mA":
            bits_pg = "00"
        elif crange == "800mA":
            bits_pg = "01"
        elif crange == "1600mA":
            bits_pg = "10"
        elif crange == "3200mA":
            bits_pg = "11"
        else:
            print(f"ERROR: I2C: INA219: wrong current-range: {crange}")

        bits_brng = "1"  # 32V FSR
        vrange = setup.get("voltage-range", "32V")
        if vrange == "16V":
            bits_brng = "0"
        elif vrange == "32V":
            bits_brng = "1"
        else:
            print(f"ERROR: I2C: INA219: wrong voltage-range: {vrange}")

        bits_adc = "1111"  # 12bit / 128 samples avg
        bits_mode = "111"  # Shunt and bus, continuous
        config_bits = f"0_0_{bits_brng}_{bits_pg}_{bits_adc}_{bits_adc}_{bits_mode}"

        self.INITS = [
            {
                "comment": "setup",
                "mode": "write",
                "value": f"{{8'd0, 16'b{config_bits}}}",
                "bytes": 3,
            },
        ]
        self.STEPS = [
            {
                "comment": "get shunt voltage",
                "mode": "write",
                "value": "{8'd1}",
                "bytes": 1,
            },
            {
                "mode": "read",
                "var": f"{self.name}_current",
                "bytes": 2,
            },
            {
                "comment": "get bus voltage",
                "mode": "write",
                "value": "{8'd2}",
                "bytes": 1,
            },
            {
                "mode": "read",
                "var": f"{self.name}_voltage",
                "bytes": 2,
            },
        ]

    def convert(self, signal_name, signal_setup, value):
        if signal_name.endswith("_valid"):
            return value
        if signal_name.endswith("_voltage"):
            return value / 2000
        return value * 1000 / 8192

    def convert_c(self, signal_name, signal_setup):
        if signal_name.endswith("_valid"):
            return ""
        if signal_name.endswith("_voltage"):
            return """
            value = value / 2000;
            """
        return """
        value = value * 1000 / 8192;
        """
