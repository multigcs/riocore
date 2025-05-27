from riocore.plugins import PluginBase


class Plugin(PluginBase):
    def setup(self):
        self.NAME = "rioencoder"
        self.INFO = "serial abs-encoder"
        self.DESCRIPTION = "abs-encoder over rs485 (rx-only)"
        self.KEYWORDS = "absolute angle bldc"
        self.ORIGIN = ""
        self.EXPERIMENTAL = True
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
            "revs": {
                "size": 32,
                "direction": "input",
            },
        }
        self.SIGNALS = {
            "angle": {
                "direction": "input",
                "format": "0.1f",
            },
            "revs": {
                "direction": "input",
                "format": "d",
            },
            "position": {
                "direction": "input",
                "format": "0.3f",
            },
        }
        self._scale = 4096

    def gateware_instances(self):
        instances = self.gateware_instances_base()
        instance = instances[self.instances_name]
        instance_parameter = instance["parameter"]
        instance_parameter["ClkFrequency"] = self.system_setup["speed"]
        return instances

    def convert(self, signal_name, signal_setup, value):
        if signal_name == "angle":
            self.SIGNALS["position"]["value"] = self.SIGNALS["revs"]["value"] * self._scale + value
            return value * 360 / self._scale

        return value

    def convert_c(self, signal_name, signal_setup):
        if signal_name == "angle":
            varname_pos = self.SIGNALS["position"]["varname"]
            varname_revs = self.SIGNALS["revs"]["varname"]
            return f"""
    float position_value = *data->{varname_revs} * {self._scale} + raw_value;
    position_value = position_value + *data->{varname_pos}_OFFSET;
    position_value = position_value / *data->{varname_pos}_SCALE;
    *data->{varname_pos} = position_value;

    value = value * 360 / {self._scale};
            """
        return ""
