from riocore.plugins import PluginBase


class Plugin(PluginBase):
    def setup(self):
        self.NAME = "quadencoder"
        self.INFO = "quadencoder"
        self.DESCRIPTION = "usable as position feedback for closed-loop configuration or as variable input to control LinuxCNC overwrites"
        self.KEYWORDS = "feedback encoder rotary linear glassscale"
        self.ORIGIN = "https://www.fpga4fun.com/QuadratureDecoder.html"
        self.VERILOGS = ["quadencoder.v"]

        self.PINDEFAULTS = {
            "a": {
                "direction": "input",
                "invert": False,
                "pull": "up",
            },
            "b": {
                "direction": "input",
                "invert": False,
                "pull": "up",
            },
        }
        self.INTERFACE = {
            "position": {
                "size": 32,
                "direction": "input",
            },
        }
        self.OPTIONS = {
            "quad_type": {
                "default": 2,
                "type": int,
                "min": 0,
                "max": 4,
                "description": "encoder type",
            },
            "rps_sum": {
                "default": 10,
                "type": int,
                "min": 0,
                "max": 100,
                "description": "number of collected values before calculate the rps value",
            },
        }

        rps_sum = self.plugin_setup.get("rps_sum", self.OPTIONS["rps_sum"]["default"])
        rps_calculation = f"""
    static uint8_t pcnt = 0;
    static float last_rpssum = 0;
    static float diff_sum = 0;
    static float duration_sum = 0.0;
    diff_sum += (raw_value - last_raw_value);
    duration_sum += *data->duration;
    pcnt++;
    if (pcnt == {rps_sum}) {{
        last_rpssum = diff_sum / duration_sum / scale;
        pcnt = 0;
        duration_sum = 0;
        diff_sum = 0;
    }}
    value_rps = last_rpssum;
        """
        self.SIGNALS = {
            "position": {
                "direction": "input",
                "targets": {
                    "rps": rps_calculation,
                    "rpm": "value_rpm = value_rps * 60.0;",
                },
                "description": "position feedback in steps",
            },
            "rps": {
                "direction": "input",
                "source": "position",
                "description": "calculates revolutions per second",
            },
            "rpm": {
                "direction": "input",
                "source": "position",
                "description": "calculates revolutions per minute",
            },
        }

        self.last_pos = 0

    def gateware_instances(self):
        instances = self.gateware_instances_base()

        instance = instances[self.instances_name]
        instance_parameter = instance["parameter"]

        quad_type = self.plugin_setup.get("quad_type", 2)
        instance_parameter["QUAD_TYPE"] = quad_type

        return instances

    def convert(self, signal_name, signal_setup, value):
        if signal_name == "position":
            scale = self.plugin_setup.get("signals", {}).get(signal_name, {}).get("scale", 1.0)

            # calc rps/rpm
            if self.duration > 0:
                diff = value - self.last_pos
                rps = diff / self.duration / scale
                self.SIGNALS["rps"]["value"] = rps
                self.SIGNALS["rpm"]["value"] = rps * 60
            self.last_pos = value

            vmin = self.plugin_setup.get("min")
            vmax = self.plugin_setup.get("max")
            if vmin is not None and value < vmin:
                value = vmin
            if vmax is not None and value > vmax:
                value = vmax
            if scale is not None:
                value *= scale
        return value

    def convert_c(self, signal_name, signal_setup):
        if signal_name == "position":
            vmin = self.plugin_setup.get("min")
            vmax = self.plugin_setup.get("max")
            scale = self.plugin_setup.get("scale", 1.0)
            if vmin is not None and vmax is not None:
                return f"""
                value *= {scale};
                if (value < {vmin}) {{
                    value = {vmin};
                }} else if (value > {vmax}) {{
                    value = {vmax};
                }}
                """
            else:
                return f"value *= {scale};"
        return ""
