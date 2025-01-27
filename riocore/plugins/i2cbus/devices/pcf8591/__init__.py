class i2c_device:
    options = {
        "info": "AD/DA converter",
        "description": "AD/DA converter 4xadc 1xdac (8bit)",
        "addresses": ["0x48", "0x49", "0x4A", "0x4B", "0x4C", "0x4D", "0x4E", "0x4F"],
    }
 
    def __init__(self, setup, system_setup={}):
        self.system_setup = system_setup
        self.name = setup["name"]
        self.addr = setup["address"]
        self.INTERFACE = {
            f"{self.name}_dac": {
                "size": 8,
                "direction": "output",
                "multiplexed": True,
            },
            f"{self.name}_adc1": {
                "size": 8,
                "direction": "input",
                "multiplexed": True,
            },
            f"{self.name}_adc2": {
                "size": 8,
                "direction": "input",
                "multiplexed": True,
            },
            f"{self.name}_adc3": {
                "size": 8,
                "direction": "input",
                "multiplexed": True,
            },
            f"{self.name}_adc4": {
                "size": 8,
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
            f"{self.name}_dac": {
                "direction": "output",
                "min": 0,
                "max": 255,
                "format": "d",
                "unit": "",
            },
            f"{self.name}_adc1": {
                "direction": "input",
                "format": "d",
                "unit": "",
            },
            f"{self.name}_adc2": {
                "direction": "input",
                "format": "d",
                "unit": "",
            },
            f"{self.name}_adc3": {
                "direction": "input",
                "format": "d",
                "unit": "",
            },
            f"{self.name}_adc4": {
                "direction": "input",
                "format": "d",
                "unit": "",
            },
            f"{self.name}_valid": {
                "direction": "input",
                "bool": True,
            },
        }
        self.PARAMS = {}

        PCF8591_DAC_FLAG = 0x40
        PCF8591_INCR_FLAG = 0x04
        self.INITS = [
            {
                "mode": "writereg",
                "values": [
                    (0x80, 0x00),
                ],
            },
        ]
        self.STEPS = [
            {
                "mode": "write",
                "value": f"{{8'd{PCF8591_DAC_FLAG}, {self.name}_dac}}",
                "bytes": 2,
            },
            {
                "mode": "write",
                "value": f"{{8'd{PCF8591_DAC_FLAG | PCF8591_INCR_FLAG | 0x00}}}",
                "bytes": 1,
            },
            {
                "mode": "read",
                "data_in": [
                    f"                                {self.name}_adc1 <= data_in[31:24];"
                    f"                                {self.name}_adc2 <= data_in[23:16];"
                    f"                                {self.name}_adc3 <= data_in[15:8];"
                    f"                                {self.name}_adc4 <= data_in[7:0];"
                ],
                "bytes": 4,
            },
        ]

    def convert(self, signal_name, signal_setup, value):
        if signal_name.endswith("_valid"):
            return value
        return value

    def convert_c(self, signal_name, signal_setup):
        if signal_name.endswith("_valid"):
            return ""
        return """
        value = value;
        """
