from riocore.plugins import PluginBase


class Plugin(PluginBase):
    def setup(self):
        self.NAME = "bitcopy"
        self.INFO = "copy a bit/pin to an other output pin"
        self.DESCRIPTION = """outputs a copy of a bit/pin

```mermaid
graph LR;
    Origin-Bit-->Origin-Modifiers-Pipeline-->Origin-Pin;
    Origin-Bit-->BitCopy-Modifiers-Pipeline-->BitCopy-Pin;

Examples:
* you can create an inverted pin for symetric signals (modifier: invert)
* or delayed signals for generating sequences (modifier: debounce with hight delay)
* make short signals visible (modifier: oneshot -> LED)

```
        """
        self.KEYWORDS = "pin bit copy"
        self.ORIGIN = ""
        self.PINDEFAULTS = {
            "bit": {
                "direction": "output",
            },
        }
        self.OPTIONS = {
            "origin": {
                "default": "ERROR",
                "type": "vpins",
                "description": "Origin Bit/Pin",
            },
        }

    def gateware_instances(self):
        instances = self.gateware_instances_base()
        origin = self.plugin_setup.get("origin", self.OPTIONS["origin"]["default"])
        for instance in instances.values():
            if "arguments" in instance:
                vname = instance["arguments"]["bit"]
                del instance["arguments"]
                instance["predefines"] = [f"assign {vname} = {origin};"]
        return instances
