from riocore.plugins import PluginBase


class Plugin(PluginBase):
    def setup(self):
        self.NAME = "demux"
        self.INFO = "binary demultiplexer"
        self.DESCRIPTION = """decodes binary values
```mermaid
graph LR;
    FPGA-Pin0-->Bin2Dec;
    FPGA-Pin1-->Bin2Dec;
    Bin2Dec-->Dec==0-->Hal-Bit0;
    Bin2Dec-->Dec==1-->Hal-Bit1;
    Bin2Dec-->Dec==2-->Hal-Bit2;
    Bin2Dec-->Dec==3-->Hal-Bit3;
```
        """
        self.KEYWORDS = "binary demultiplexer"
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

        for bit in range(2 ** bits):
            self.INTERFACE[f"bit{bit}"] = {
                "size": 1,
                "direction": "input",
            }
            self.SIGNALS[f"bit{bit}"] = {
                "direction": "input",
            }

        for bit in range(bits):
            self.PINDEFAULTS[f"pin{bit}"] = {
                "direction": "input",
            }

    def gateware_instances(self):
        instances = self.gateware_instances_base()
        bits = self.plugin_setup.get("bits", self.OPTIONS["bits"]["default"])

        for instance in instances.values():
            instance["predefines"] = []
            decname = f"DECVAL_{self.instances_name.upper()}"
            if "arguments" in instance:
                bitlist = []
                for bit in range(bits):
                    pinname = instance["arguments"][f"pin{bit}"]
                    bitlist.append(pinname)
                instance["predefines"] += [f"wire {decname};", f"assign {decname} = {{{', '.join(reversed(bitlist))}}};"]

                for bit in range(2 ** bits):
                    bitname = instance["arguments"][f"bit{bit}"]
                    print(bit, bitname)
                    instance["predefines"] += [f"assign {bitname} = ({decname} == {bit});"]

        del instance["arguments"]
        return instances



