from riocore.plugins import PluginBase


class Plugin(PluginBase):
    def setup(self):
        self.NAME = "binin"
        self.INFO = "binary to decimal input"
        self.DESCRIPTION = """reads binary values
```mermaid
graph LR;
    FPGA-Pin0-->Bin2Dec;
    FPGA-Pin1-->Bin2Dec;
    Bin2Dec-->Hal-Value;
```
        """
        self.KEYWORDS = "binary bin2dec"
        self.ORIGIN = ""
        self.PINDEFAULTS = {}

        self.OPTIONS = {
            "bits": {
                "default": 4,
                "type": int,
                "min": 1,
                "max": 32,
                "unit": "bits",
                "description": "number of inputs",
            },
        }

        bits = self.plugin_setup.get("bits", self.OPTIONS["bits"]["default"])

        self.INTERFACE = {
            "value": {
                "size": int((bits + 7) // 8 * 8),
                "direction": "input",
            },
        }
        self.SIGNALS = {
            "value": {
                "direction": "input",
            },
        }

        for bit in range(bits):
            self.PINDEFAULTS[f"bin{bit}"] = {
                "direction": "input",
            }

    def gateware_instances(self):
        instances = self.gateware_instances_base()
        bits = self.plugin_setup.get("bits", self.OPTIONS["bits"]["default"])

        for instance in instances.values():
            if "arguments" in instance:
                valuename = instance["arguments"]["value"]
                bitlist = []
                for bit in range(bits):
                    vname = instance["arguments"][f"bin{bit}"]
                    bitlist.append(vname)

                instance["predefines"] = [f"assign {valuename} = {{{', '.join(reversed(bitlist))}}};"]
                del instance["arguments"]
        return instances
