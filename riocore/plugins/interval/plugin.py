from riocore.plugins import PluginBase


class Plugin(PluginBase):
    def setup(self):
        self.NAME = "interval"
        self.INFO = "interval timer"
        self.DESCRIPTION = "to control things like lubric pumps"
        self.KEYWORDS = ""
        self.ORIGIN = ""
        self.EXPERIMENTAL = True
        self.VERILOGS = ["interval.v"]
        self.PINDEFAULTS = {
            "out": {
                "direction": "output",
            },
        }
        self.INTERFACE = {
            "enable": {
                "size": 1,
                "direction": "output",
                "multiplexed": True,
            },
            "ontime": {
                "size": 24,
                "direction": "output",
                "multiplexed": True,
            },
            "interval": {
                "size": 24,
                "direction": "output",
                "multiplexed": True,
            },
        }
        self.SIGNALS = {
            "enable": {
                "direction": "output",
                "bool": True,
            },
            "ontime": {
                "direction": "output",
                "unit": "seconds",
                "min": 0,
                "default": 1,
            },
            "interval": {
                "direction": "output",
                "unit": "seconds",
                "min": 0,
                "default": 10,
            },
        }

    def gateware_instances(self):
        instances = self.gateware_instances_base()
        instance = instances[self.instances_name]
        instance_parameter = instance["parameter"]
        instance_parameter["DIVIDER"] = self.system_setup["speed"]
        return instances
