from riocore.plugins import PluginBase


class Plugin(PluginBase):
    def setup(self):
        self.NAME = "pinroute"
        self.INFO = ""
        self.DESCRIPTION = ""
        self.KEYWORDS = ""
        self.ORIGIN = ""
        self.PINDEFAULTS = {
            "out": {
                "direction": "output",
            },
        }
        self.OPTIONS = {
            "inputs": {
                "default": 2,
                "type": int,
                "description": "number of inputs",
            },
        }

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

        for input_n in range(num_inputs):
            self.PINDEFAULTS[f"in{input_n}"] = {
                "direction": "input",
            }

    def gateware_instances(self):
        instances = self.gateware_instances_base()
        num_inputs = self.plugin_setup.get("inputs", 2)

        for instance in instances.values():
            if "arguments" in instance:
                verilog = []
                inputvar = instance["arguments"]["input"]
                outarg = instance["arguments"]["out"]
                verilog.append(f"reg {outarg} = 0;")
                verilog.append("always @(posedge sysclk) begin")

                verilog.append(f"    case ({inputvar})")
                for input_n in range(num_inputs):
                    inarg = instance["arguments"][f"in{input_n}"]
                    verilog.append(f"        {input_n}: begin")
                    verilog.append(f"            {outarg} <= {inarg};")
                    verilog.append("        end")
                verilog.append(f"        default: begin")
                verilog.append(f"            {outarg} <= 0;")
                verilog.append("        end")
                verilog.append("    endcase")
                verilog.append("end")
                verilog.append("")
                instance["predefines"] = verilog
                del instance["arguments"]
        return instances
