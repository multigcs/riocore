import time

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
            "revs": {
                "size": 32,
                "direction": "input",
            },
            "angle": {
                "size": 16,
                "direction": "input",
            },
            "temperature": {
                "size": 16,
                "direction": "input",
            },
        }
        self.SIGNALS = {
            "revs": {
                "direction": "input",
                "format": "d",
            },
            "angle": {
                "direction": "input",
                "format": "0.1f",
            },
            "temperature": {
                "direction": "input",
                "unit": "°C",
                "format": "0.1f",
            },
            "position": {
                "direction": "input",
                "format": "0.3f",
            },
            "rps": {
                "direction": "input",
                "format": "0.3f",
            },
            "rpm": {
                "direction": "input",
                "format": "0.3f",
            },
        }
        self._scale = 4096
        self.position_last = 0
        self.timer_last = time.time()

    def gateware_instances(self):
        instances = self.gateware_instances_base()
        instance = instances[self.instances_name]
        instance_parameter = instance["parameter"]
        instance_parameter["ClkFrequency"] = self.system_setup["speed"]
        return instances

    def convert(self, signal_name, signal_setup, value):
        if signal_name == "temperature":
            return value / 10
        elif signal_name == "angle":
            position = self.SIGNALS["revs"]["value"] * self._scale + value
            self.SIGNALS["position"]["value"] = position

            # calc rps/rpm
            diff = position - self.position_last
            self.position_last = position
            timer_new = time.time()
            timer_diff = timer_new - self.timer_last
            rps = diff / timer_diff / 4096
            self.timer_last = timer_new
            self.SIGNALS["rps"]["value"] = rps
            self.SIGNALS["rpm"]["value"] = rps * 60

            return value * 360 / self._scale
        return value

    def convert_c(self, signal_name, signal_setup):
        if signal_name == "temperature":
            return "value = value / 10;"
        elif signal_name == "angle":
            varname_revs = self.SIGNALS["revs"]["varname"]
            varname_pos = self.SIGNALS["position"]["varname"]
            varname_rps = self.SIGNALS["rps"]["varname"]
            varname_rpm = self.SIGNALS["rpm"]["varname"]
            return f"""

    // calc position
    float position_value = *data->{varname_revs} * {self._scale} + raw_value;

    // calc rps/rpm
    static uint8_t pcnt = 0;
    static float last_rpssum = 0;
    static float last_pos = 0;
    static float diff_sum = 0;
    static float duration_sum = 0.0;
    float diff = position_value - last_pos;
    last_pos = position_value;
    diff_sum += diff;
    duration_sum += *data->duration;
    pcnt++;
    if (pcnt == 100) {{
        last_rpssum = diff_sum / duration_sum / 4096;
        pcnt = 0;
        duration_sum = 0;
        diff_sum = 0;
    }}
    *data->{varname_rps} = last_rpssum;
    *data->{varname_rpm} = last_rpssum * 60;

    // pos scale/offset
    position_value = position_value + *data->{varname_pos}_OFFSET;
    position_value = position_value / *data->{varname_pos}_SCALE;
    *data->{varname_pos} = position_value;

    // calc angle (0-360°)
    value = value * 360 / {self._scale};
            """
        return ""
