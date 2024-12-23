from riocore.plugins import PluginBase


class Plugin(PluginBase):
    def setup(self):
        self.NAME = "binout"
        self.INFO = "decimal to binary output"
        self.DESCRIPTION = """outputs binary values
```mermaid
graph LR;
    Hal-Value-->Dec2Bin;
    Dec2Bin-->FPGA-Pin0;
    Dec2Bin-->FPGA-Pin1;
```
        """
        self.KEYWORDS = "binary dec2bin r2r-dac"
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
                "direction": "output",
            },
        }
        self.SIGNALS = {
            "value": {
                "direction": "output",
            },
        }

        for bit in range(bits):
            self.PINDEFAULTS[f"bin{bit}"] = {
                "direction": "output",
            }

    def gateware_instances(self):
        instances = self.gateware_instances_base()
        bits = self.plugin_setup.get("bits", self.OPTIONS["bits"]["default"])

        for instance in instances.values():
            if "arguments" in instance:
                valuename = instance["arguments"]["value"]
                assignlist = []
                for bit in range(bits):
                    if f"bin{bit}" in instance["arguments"]:
                        vname = instance["arguments"][f"bin{bit}"]
                        assignlist.append(f"assign {vname} = {valuename}[{bit}];")
                    else:
                        print(f"ERROR: binout: pin for bit {bit} not found")

                instance["predefines"] = assignlist
                del instance["arguments"]
        return instances
