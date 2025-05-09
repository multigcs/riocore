from riocore.plugins import PluginBase


class Plugin(PluginBase):
    def setup(self):
        self.NAME = "as5600pwm"
        self.INFO = "as5600 pwm input"
        self.DESCRIPTION = "scale: 4096"
        self.KEYWORDS = "absolute encoder with pwm output"
        self.ORIGIN = ""
        self.VERILOGS = ["as5600pwm.v"]
        self.PINDEFAULTS = {
            "pwm": {
                "direction": "input",
                "invert": False,
                "pull": None,
            },
        }
        self.INTERFACE = {
            "angle": {
                "size": 16,
                "direction": "input",
            },
            "valid": {
                "size": 1,
                "direction": "input",
            },
        }
        self.SIGNALS = {
            "angle": {
                "direction": "input",
                "unit": "ms",
                "format": "0.4f",
            },
            "position": {
                "direction": "input",
                "format": "0.1f",
            },
            "valid": {
                "direction": "input",
                "bool": True,
            },
        }
        self.last = 0
        self.revs = 0
        self.scale = 4096

    def gateware_instances(self):
        instances = self.gateware_instances_base()
        instance = instances[self.instances_name]
        instance_parameter = instance["parameter"]
        instance_parameter["DIVIDER"] = int(self.system_setup["speed"] / (self.scale - 128 - 128) / 32)
        return instances

    def convert(self, signal_name, signal_setup, value):
        if signal_name == "angle":
            new = value
            diff = new - self.last
            if diff < -2048:
                self.revs += 1
            elif diff > 2048:
                self.revs -= 1
            self.SIGNALS["position"]["value"] = (self.revs * self.scale) + new
            self.last = new

            return value * 360 / self.scale

        return value

    def convert_c(self, signal_name, signal_setup):
        if signal_name == "angle":
            varname = self.SIGNALS["position"]["varname"]
            return f"""

    static float revs = 0;
    float diff = 0;

    diff = raw_value - last_raw_value;

    if (diff < -2048) {{
        revs++;
    }} else if (diff > 2048) {{
        revs--;
    }}

    float position_value = (revs * {self.scale}) + raw_value;
    position_value = position_value + *data->{varname}_OFFSET;
    position_value = position_value / *data->{varname}_SCALE;
    *data->{varname} = position_value;

    value = value * 360 / {self.scale};
            """
        return ""
