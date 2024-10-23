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
        }
        self.SIGNALS = {
            "position": {
                "direction": "input",
                "targets": {
                    "rps": "value_rps = (raw_value - last_raw_value) * *data->duration / scale;",
                    "rpm": "value_rpm = (raw_value - last_raw_value) * *data->duration * 60.0 / scale;",
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

    def gateware_instances(self):
        instances = self.gateware_instances_base()

        instance = instances[self.instances_name]
        instance_parameter = instance["parameter"]

        quad_type = self.plugin_setup.get("quad_type", 2)
        instance_parameter["QUAD_TYPE"] = quad_type

        return instances

    def convert(self, signal_name, signal_setup, value):
        if signal_name == "position":
            vmin = self.plugin_setup.get("min")
            vmax = self.plugin_setup.get("max")
            scale = self.plugin_setup.get("scale", 1.0)
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
