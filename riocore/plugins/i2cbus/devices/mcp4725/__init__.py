class i2c_device:
    options = {
        "info": "12-bit DAC",
        "description": "12-Bit Digital-to-Analog Converter with EEPROM Memory",
        "addresses": ["0x60", "0x61", "0x62", "0x63", "0x64", "0x65", "0x66", "0x67"],
    }

    def __init__(self, setup, system_setup={}):
        self.system_setup = system_setup
        self.name = setup["name"]
        self.addr = setup["address"]
        self.INTERFACE = {
            f"{self.name}_voltage": {
                "size": 16,
                "direction": "output",
            },
            f"{self.name}_valid": {
                "size": 1,
                "direction": "input",
                "multiplexed": True,
            },
        }
        self.SIGNALS = {
            f"{self.name}_voltage": {
                "direction": "output",
                "min": 0,
                "max": 3300,
                "format": "d",
                "unit": "mV",
            },
            f"{self.name}_valid": {
                "direction": "input",
                "bool": True,
            },
        }
        
        MCP4725_CMD_WRITEDAC = 0x40
        MCP4725_CMD_WRITEDACEEPROM = 0x60
        
        self.PARAMS = {}
        self.INITS = []
        self.STEPS = [
            {
                "comment": "write data in fast-mode",
                "mode": "write",
                "value": f"{{4'b0000, {self.name}_voltage[11:0]}}",
                "bytes": 2,
            },
        ]

    def convert(self, signal_name, signal_setup, value):
        if signal_name.endswith("_valid"):
            return value
        return value * 4095 / 3300

    def convert_c(self, signal_name, signal_setup):
        if signal_name.endswith("_valid"):
            return ""
        return """
        value = value * 4095 / 3300;
        """
