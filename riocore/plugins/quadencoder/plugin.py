from riocore.plugins import PluginBase


class Plugin(PluginBase):
    def setup(self):
        self.NAME = "quadencoder"
        self.VERILOGS = ["quadencoder.v"]
        self.PINDEFAULTS = {
            "a": {
                "direction": "input",
                "invert": False,
                "pullup": True,
            },
            "b": {
                "direction": "input",
                "invert": False,
                "pullup": True,
            },
        }
        self.INTERFACE = {
            "position": {
                "size": 32,
                "direction": "input",
            },
        }
        self.SIGNALS = {
            "position": {
                "direction": "input",
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
