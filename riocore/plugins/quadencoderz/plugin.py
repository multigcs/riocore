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
            "index_enable": {
                "size": 1,
                "direction": "output",
            },
            "index_out": {
                "size": 1,
                "direction": "input",
            },
            "position": {
                "size": 32,
                "direction": "input",
            },
        }
        self.SIGNALS = {
            "index_enable": {
                "direction": "output",
                "bool": True,
            },
            "index_out": {
                "direction": "input",
                "bool": True,
            },
            "position": {
                "direction": "input",
            },
        }

    def gateware_instances(self):
        instances = self.gateware_instances_base()
        instance = instances[self.instances_name]
        instance_predefines = instance["predefines"]
        instance_parameter = instance["parameter"]
        instance_arguments = instance["arguments"]
        quad_type = self.plugin_setup.get("quad_type", 2)
        instance_parameter["QUAD_TYPE"] = quad_type
        return instances
