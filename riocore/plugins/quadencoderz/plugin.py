from riocore.plugins import PluginBase


class Plugin(PluginBase):
    def setup(self):
        self.NAME = "quadencoderz"
        self.INFO = "quadencoder with index pin"
        self.DESCRIPTION = "usable as spindle-encoder for rigid tapping and thread cutting"
        self.KEYWORDS = "feedback encoder rotary linear glassscale  index"
        self.ORIGIN = "https://www.fpga4fun.com/QuadratureDecoder.html"
        self.VERILOGS = ["quadencoderz.v"]
        self.PINDEFAULTS = {
            "a": {
                "direction": "input",
                "invert": False,
                "pull": None,
            },
            "b": {
                "direction": "input",
                "invert": False,
                "pull": None,
            },
            "z": {
                "description": "index pin",
                "direction": "input",
                "invert": False,
                "pull": None,
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
        self.INTERFACE = {
            "indexenable": {
                "size": 1,
                "direction": "output",
            },
            "indexout": {
                "size": 1,
                "direction": "input",
            },
            "position": {
                "size": 32,
                "direction": "input",
            },
        }
        self.SIGNALS = {
            "indexenable": {
                "is_index_enable": True,
                "direction": "inout",
                "bool": True,
            },
            "indexout": {
                "is_index_out": True,
                "direction": "input",
                "bool": True,
            },
            "position": {
                "is_index_position": True,
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
        instance["predefines"]
        instance_parameter = instance["parameter"]
        instance["arguments"]
        quad_type = self.plugin_setup.get("quad_type", self.OPTIONS["quad_type"]["default"])
        instance_parameter["QUAD_TYPE"] = quad_type
        return instances
