class i2c_device:
    options = {
        "info": "3channel current and voltage monitor",
        "description": "3 channel, high-side current and bus voltage monitor",
        "addresses": ["0x40", "0x41", "0x42", "0x43"],
    }

    def __init__(self, setup, system_setup={}):
        self.system_setup = system_setup
        self.name = setup["name"]
        self.addr = setup["address"]
        self.INTERFACE = {
            f"{self.name}_current1": {
                "size": 16,
                "direction": "input",
                "multiplexed": True,
            },
            f"{self.name}_voltage1": {
                "size": 16,
                "direction": "input",
                "multiplexed": True,
            },
            f"{self.name}_current2": {
                "size": 16,
                "direction": "input",
                "multiplexed": True,
            },
            f"{self.name}_voltage2": {
                "size": 16,
                "direction": "input",
                "multiplexed": True,
            },
            f"{self.name}_current3": {
                "size": 16,
                "direction": "input",
                "multiplexed": True,
            },
            f"{self.name}_voltage3": {
                "size": 16,
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
            f"{self.name}_current1": {
                "direction": "input",
                "format": "0.1f",
                "unit": "mA",
            },
            f"{self.name}_voltage1": {
                "direction": "input",
                "format": "0.1f",
                "unit": "V",
            },
            f"{self.name}_current2": {
                "direction": "input",
                "format": "0.1f",
                "unit": "mA",
            },
            f"{self.name}_voltage2": {
                "direction": "input",
                "format": "0.1f",
                "unit": "V",
            },
            f"{self.name}_current3": {
                "direction": "input",
                "format": "0.1f",
                "unit": "mA",
            },
            f"{self.name}_voltage3": {
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

        bits_en = "111"  # all channels enabled
        bits_avg = "001"  # 4x AVG
        bits_vbct = "111"  # 8.244ms (slow)
        bits_mode = "111"  # Shunt and bus, continuous
        config_bits = f"0_{bits_en}_{bits_avg}_{bits_vbct}_{bits_vbct}_{bits_mode}"

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
                "comment": "get shunt voltage1",
                "mode": "write",
                "value": "{8'd1}",
                "bytes": 1,
            },
            {
                "mode": "read",
                "var": f"{self.name}_current1",
                "bytes": 2,
            },
            {
                "comment": "get bus voltage1",
                "mode": "write",
                "value": "{8'd2}",
                "bytes": 1,
            },
            {
                "mode": "read",
                "var": f"{self.name}_voltage1",
                "bytes": 2,
            },
            {
                "comment": "get shunt voltage2",
                "mode": "write",
                "value": "{8'd3}",
                "bytes": 1,
            },
            {
                "mode": "read",
                "var": f"{self.name}_current2",
                "bytes": 2,
            },
            {
                "comment": "get bus voltage2",
                "mode": "write",
                "value": "{8'd4}",
                "bytes": 1,
            },
            {
                "mode": "read",
                "var": f"{self.name}_voltage2",
                "bytes": 2,
            },
            {
                "comment": "get shunt voltage3",
                "mode": "write",
                "value": "{8'd5}",
                "bytes": 1,
            },
            {
                "mode": "read",
                "var": f"{self.name}_current3",
                "bytes": 2,
            },
            {
                "comment": "get bus voltage3",
                "mode": "write",
                "value": "{8'd6}",
                "bytes": 1,
            },
            {
                "mode": "read",
                "var": f"{self.name}_voltage3",
                "bytes": 2,
            },
        ]

    def convert(self, signal_name, signal_setup, value):
        if signal_name.endswith("_valid"):
            return value
        elif signal_name.endswith("_current1"):
            return value / 20
        elif signal_name.endswith("_voltage1"):
            return value / 1000
        elif signal_name.endswith("_current2"):
            return value / 20
        elif signal_name.endswith("_voltage2"):
            return value / 1000
        elif signal_name.endswith("_current3"):
            return value / 20
        elif signal_name.endswith("_voltage3"):
            return value / 1000
        return value

    def convert_c(self, signal_name, signal_setup):
        if signal_name.endswith("_valid"):
            return "value = value / 1000;"
        elif signal_name.endswith("_current1"):
            return "value = value / 20;"
        elif signal_name.endswith("_voltage1"):
            return "value = value / 1000;"
        elif signal_name.endswith("_current2"):
            return "value = value / 20;"
        elif signal_name.endswith("_voltage2"):
            return "value = value / 1000;"
        elif signal_name.endswith("_current3"):
            return "value = value / 20;"
        elif signal_name.endswith("_voltage3"):
            return "value = value / 1000;"
        return ""
