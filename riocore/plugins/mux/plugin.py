from riocore.plugins import PluginBase


class Plugin(PluginBase):
    def setup(self):
        self.NAME = "mux"
        self.INFO = "binary multiplexer"
        self.DESCRIPTION = """encodes binary values"""
        self.KEYWORDS = "binary multiplexer"
        self.ORIGIN = ""
        self.PINDEFAULTS = {}
        self.INTERFACE = {}
        self.SIGNALS = {}

        self.OPTIONS = {
            "bits": {
                "default": 2,
                "type": int,
                "min": 1,
                "max": 32,
                "unit": "bits",
                "description": "number of inputs",
            },
        }

        bits = self.plugin_setup.get("bits", self.OPTIONS["bits"]["default"])

        for bit in range(bits):
            self.INTERFACE[f"bit{bit}"] = {
                "size": 1,
                "direction": "output",
            }
            self.SIGNALS[f"bit{bit}"] = {
                "direction": "output",
                "bool": True,
            }

        for bit in range(2**bits):
            self.PINDEFAULTS[f"pin{bit}"] = {
                "direction": "output",
            }

    def gateware_instances(self):
        instances = self.gateware_instances_base()
        bits = self.plugin_setup.get("bits", self.OPTIONS["bits"]["default"])

        for instance in instances.values():
            decname = f"DECVAL_{self.instances_name.upper()}"
            if "arguments" in instance:
                instance["predefines"] = []
                bitlist = []
                for bit in range(bits):
                    pinname = instance["arguments"][f"bit{bit}"]
                    bitlist.append(pinname)
                instance["predefines"] += [f"wire [{bits - 1}:0] {decname};", f"assign {decname} = {{{', '.join(reversed(bitlist))}}};"]

                for bit in range(2**bits):
                    bitname = instance["arguments"][f"pin{bit}"]
                    instance["predefines"] += [f"wire {bitname};", f"assign {bitname} = ({decname} == {bit});"]
                del instance["arguments"]

        return instances
