from riocore.plugins import PluginBase


class Plugin(PluginBase):
    def setup(self):
        self.NAME = "rioencoder"
        self.INFO = "serial abs-encoder"
        self.DESCRIPTION = "abs-encoder over rs485 (rx-only)"
        self.KEYWORDS = "absolute angle bldc"
        self.ORIGIN = ""
        self.VERILOGS = ["rioencoder.v", "uart_baud.v", "uart_rx.v"]
        self.PINDEFAULTS = {
            "rx": {
                "direction": "input",
            },
            "rw": {
                "direction": "output",
                "optional": True,
            },
        }
        self.INTERFACE = {
            "angle": {
                "size": 16,
                "direction": "input",
            },
        }
        self.SIGNALS = {
            "angle": {
                "direction": "input",
            },
            "position": {
                "direction": "input",
                "format": "0.1f",
            },
        }
        self.last = 0
        self.revs = 0
        self.scale = 4096

    def gateware_instances(self):
        instances = self.gateware_instances_base()
        instance = instances[self.instances_name]
        instance_parameter = instance["parameter"]
        instance_parameter["ClkFrequency"] = self.system_setup["speed"]
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
