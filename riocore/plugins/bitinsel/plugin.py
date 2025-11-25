import copy

from riocore.plugins import PluginBase


class Plugin(PluginBase):
    def setup(self):
        self.NAME = "bitinsel"
        self.INFO = "input selector / demultiplexer"
        self.DESCRIPTION = """input selector / demultiplexer with data pin"""
        self.KEYWORDS = ""
        self.ORIGIN = ""
        self.VERILOGS = ["bitinsel.v"]
        self.TYPE = "expansion"
        self.PINDEFAULTS = {
            "bit_in": {
                "direction": "input",
            },
        }
        self.INTERFACE = {}
        self.SIGNALS = {}

        self.OPTIONS = {
            "speed": {
                "default": 1000000,
                "type": int,
                "min": 100000,
                "max": 10000000,
                "description": "interface clock",
            },
            "bits": {
                "default": 4,
                "type": int,
                "min": 1,
                "max": 32,
                "unit": "bits",
                "description": "number of selector bits",
            },
        }

        bits = self.plugin_setup.get("bits", self.OPTIONS["bits"]["default"])

        self.BITS_IN = 2**bits
        self.BITS_OUT = 0

        for bit in range(bits):
            self.PINDEFAULTS[f"addr{bit}"] = {
                "direction": "output",
            }

    def gateware_instances(self):
        instances = self.gateware_instances_base()
        instance = instances[self.instances_name]
        instance_parameter = instance["parameter"]
        instance_arguments = instance["arguments"]

        speed = int(self.plugin_setup.get("speed", self.OPTIONS["speed"]["default"]))
        bits = int(self.plugin_setup.get("bits", self.OPTIONS["bits"]["default"]))
        divider = int(self.system_setup["speed"] / speed / 3.3)
        instance_parameter["DIVIDER"] = divider
        instance_parameter["WIDTH"] = bits
        instance_parameter["BITS"] = 2**bits

        addrs = []
        for arg, adata in copy.deepcopy(instance_arguments).items():
            if arg.startswith("addr"):
                addrs.append(adata)
                del instance_arguments[arg]
        instance_arguments["addr"] = f"{{{', '.join(reversed(addrs))}}}"
        del instance_arguments["data_out"]

        return instances
