from riocore.plugins import PluginBase


class Plugin(PluginBase):
    def setup(self):
        self.NAME = "caliper"
        self.INFO = "reading position from cheap calipers"
        self.DESCRIPTION = """warning, there are different protocols
and also some without output
* rate: ~8Hz (123ms)
* too slow for joint feedback
both on the image are working
"""
        self.KEYWORDS = ""
        self.ORIGIN = ""
        self.VERILOGS = ["caliper.v"]
        self.PINDEFAULTS = {
            "data": {
                "direction": "input",
            },
            "clock": {
                "direction": "input",
            },
        }
        self.INTERFACE = {
            "position": {
                "size": 24,
                "direction": "input",
            },
            "mode": {
                "size": 1,
                "direction": "input",
            },
        }
        self.SIGNALS = {
            "position": {
                "direction": "input",
                "unit": "mm",
                "format": "0.2f",
            },
            "mode": {
                "direction": "input",
                "bool": True,
                "unit": "mm/inch",
            },
        }

    def gateware_instances(self):
        instances = self.gateware_instances_base()
        instance = instances[self.instances_name]
        instance_parameter = instance["parameter"]
        timeout = self.system_setup["speed"] // 1000 * 1  # 1 ms
        instance_parameter["TIMEOUT"] = timeout
        return instances

    def convert(self, signal_name, signal_setup, value):
        print(signal_name, f"{value} {value:b}")
        if signal_name == "position":
            if value >= 1048576:
                value = 1048576 - value
            if self.signals()["mode"]["value"] == 0:
                return value / 100.0
            else:
                return value / 2000.0 * 25.4
        return value

    def convert_c(self, signal_name, signal_setup):
        if signal_name == "position":
            return f"""
    if (value >= 1048576) {{
        value = 1048576 - value;
    }}
    if (data->VARIN1_{signal_setup["var_prefix"]}_MODE == 0) {{
        value /= 100.0;
    }} else {{
        value = value / 2000.0 * 25.4;
    }}
            """
        return ""
