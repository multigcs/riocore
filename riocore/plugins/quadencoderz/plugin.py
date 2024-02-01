from riocore.plugins import PluginBase


class Plugin(PluginBase):
    def setup(self):
        self.NAME = "quadencoderz"
        self.VERILOGS = ["quadencoderz.v"]
        self.PINDEFAULTS = {
            "a": {
                "direction": "input",
                "invert": False,
                "pullup": False,
            },
            "b": {
                "direction": "input",
                "invert": False,
                "pullup": False,
            },
            "z": {
                "direction": "input",
                "invert": False,
                "pullup": False,
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
            },
            "rps": {
                "direction": "input",
                "source": "position",
            },
            "rpm": {
                "direction": "input",
                "source": "position",
            },
        }
        self.INFO = "quadencoder with index pin"
        self.DESCRIPTION = ""

    def gateware_instances(self):
        instances = self.gateware_instances_base()
        instance = instances[self.instances_name]
        instance_predefines = instance["predefines"]
        instance_parameter = instance["parameter"]
        instance_arguments = instance["arguments"]
        quad_type = self.plugin_setup.get("quad_type", 2)
        instance_parameter["QUAD_TYPE"] = quad_type
        return instances
