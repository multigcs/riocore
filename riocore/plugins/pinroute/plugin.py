from riocore.plugins import PluginBase


class Plugin(PluginBase):
    def setup(self):
        self.NAME = "pinroute"
        self.INFO = "routing one output pin to multiple inputs"
        self.DESCRIPTION = ""
        self.KEYWORDS = ""
        self.GRAPH = """
graph LR;
    In0-->Routing;
    In1-->Routing;
    Routing-->Out;
        """
        self.ORIGIN = ""
        self.PINDEFAULTS = {}
        self.OPTIONS = {
            "inputs": {
                "default": 2,
                "type": int,
                "min": 2,
                "max": 100,
                "description": "number of inputs",
            },
            "channels": {
                "default": 1,
                "type": int,
                "min": 1,
                "max": 16,
                "description": "number of channels",
            },
        }

        num_channels = self.plugin_setup.get("channels", 1)
        num_inputs = self.plugin_setup.get("inputs", 2)

        self.INTERFACE = {
            "input": {
                "size": 8,
                "multiplexed": True,
                "direction": "output",
            },
        }
        self.SIGNALS = {
            "input": {
                "direction": "output",
                "min": 0,
                "max": num_inputs - 1,
                "description": "input selector",
            },
        }

        for channels_n in range(num_channels):
            char = chr(65 + channels_n)
            self.PINDEFAULTS[f"out{char}"] = {
                "direction": "output",
            }

            for input_n in range(num_inputs):
                self.PINDEFAULTS[f"in{char}{input_n}"] = {
                    "direction": "input",
                }

    def gateware_instances(self):
        instances = self.gateware_instances_base()
        num_inputs = self.plugin_setup.get("inputs", 2)
        num_channels = self.plugin_setup.get("channels", 1)

        for instance in instances.values():
            if "arguments" in instance:
                verilog = []
                inputvar = instance["arguments"]["input"]
                for channels_n in range(num_channels):
                    char = chr(65 + channels_n)
                    outarg = instance["arguments"][f"out{char}"]
                    verilog.append(f"reg {outarg} = 0;")
                verilog.append("always @(posedge sysclk) begin")
                verilog.append(f"    case ({inputvar})")
                for input_n in range(num_inputs):
                    verilog.append(f"        {input_n}: begin")
                    for channels_n in range(num_channels):
                        char = chr(65 + channels_n)
                        outarg = instance["arguments"][f"out{char}"]
                        inarg = instance["arguments"][f"in{char}{input_n}"]
                        verilog.append(f"            {outarg} <= {inarg};")
                    verilog.append("        end")
                verilog.append("        default: begin")
                for channels_n in range(num_channels):
                    char = chr(65 + channels_n)
                    outarg = instance["arguments"][f"out{char}"]
                    verilog.append(f"            {outarg} <= 0;")
                verilog.append("        end")
                verilog.append("    endcase")
                verilog.append("end")
                verilog.append("")
                instance["predefines"] = verilog
                del instance["arguments"]
        return instances
