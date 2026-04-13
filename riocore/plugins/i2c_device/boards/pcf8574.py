from PyQt5.QtCore import Qt


class i2c_device:
    options = {
        "info": "8bit io-expander",
        "description": "",
        "addresses": ["0x20", "0x21", "0x22", "0x23", "0x24", "0x25", "0x26", "0x27"],
        "config": {
            "bitvar": {
                "type": bool,
                "description": "use as single bits",
                "default": True,
            },
            "expansion": {
                "type": bool,
                "description": "use as expansion io",
                "default": False,
            },
            "inputs": {
                "type": "bits",
                "min": 0,
                "max": 255,
                "description": "use as input",
                "default": 255,
                "width": 8,
            },
            "outputs": {
                "type": "bits",
                "min": 0,
                "max": 255,
                "description": "use as output",
                "default": 255,
                "width": 8,
            },
        },
    }

    def __init__(self, parent, system_setup=None):
        self.system_setup = system_setup or {}
        self.name = parent.instances_name
        setup = parent.plugin_setup
        self.speed = 400000
        self.bitvar = setup.get("bitvar", self.options["config"]["bitvar"]["default"])
        self.inputs = setup.get("inputs", self.options["config"]["inputs"]["default"])
        self.outputs = setup.get("outputs", self.options["config"]["outputs"]["default"])
        self.address = setup.get("address", "0x20")
        expansion = setup.get("expansion", self.options["config"]["expansion"]["default"])
        self.INTERFACE = {}
        self.SIGNALS = {}
        setup_data_in = []
        setup_value = None
        if expansion is True:
            self.default = 255
        if self.bitvar:
            # write single bits into data_out byte
            bitlist = []
            for bit in range(8):
                if (1 << bit) & self.outputs:
                    bitlist.append(f"{self.name}_out{bit}")
                else:
                    bitlist.append("1'd1")

            setup_value = f"{{{', '.join(reversed(bitlist))}}}"

            # write data_in into single bits
            for bit in range(8):
                if (1 << bit) & self.inputs:
                    setup_data_in.append(f"                                {self.name}_in{bit} <= data_in[{bit}];")

            for bit in range(8):
                if (1 << bit) & self.inputs:
                    self.INTERFACE[f"in{bit}"] = {
                        "size": 1,
                        "direction": "input",
                    }
                    self.SIGNALS[f"in{bit}"] = {
                        "direction": "input",
                        "bool": True,
                        "interface": f"in{bit}",
                    }

                if (1 << bit) & self.outputs:
                    self.INTERFACE[f"out{bit}"] = {
                        "size": 1,
                        "direction": "output",
                    }
                    self.SIGNALS[f"out{bit}"] = {
                        "direction": "output",
                        "bool": True,
                        "interface": f"out{bit}",
                    }
        else:
            self.INTERFACE["in"] = {
                "size": 8,
                "direction": "input",
            }
            self.INTERFACE["out"] = {
                "size": 8,
                "direction": "output",
            }
            self.SIGNALS["in"] = {
                "direction": "input",
                "min": 0,
                "max": 255,
                "interface": "in",
            }
            self.SIGNALS["out"] = {
                "direction": "output",
                "min": 0,
                "max": 255,
                "interface": "out",
            }
        self.INTERFACE["valid"] = {
            "size": 1,
            "direction": "input",
        }
        self.SIGNALS["valid"] = {
            "direction": "input",
            "bool": True,
            "interface": "valid",
        }
        self.PINDEFAULTS = {
            "I2C": {"direction": "output", "edge": "target", "pos": [10, 35], "type": ["I2C"], "bus": True},
            "I2C:OUT": {"direction": "output", "edge": "source", "pos": [200, 35], "type": ["PASSTHROUGH"], "bus": True, "pintype": "PASSTHROUGH", "source": "I2C"},
        }
        if expansion:
            for bit in range(8):
                if (1 << bit) & self.outputs and (1 << bit) & self.inputs:
                    self.PINDEFAULTS[f"IO:P{bit}"] = {"direction": "all", "edge": "source", "pos": [int(130 - bit * 11), 7], "type": ["FPGA"]}
                elif (1 << bit) & self.outputs:
                    self.PINDEFAULTS[f"IO:P{bit}"] = {"direction": "output", "edge": "source", "pos": [int(130 - bit * 11), 7], "type": ["FPGA"]}
                elif (1 << bit) & self.inputs:
                    self.PINDEFAULTS[f"IO:P{bit}"] = {"direction": "input", "edge": "source", "pos": [int(130 - bit * 11), 7], "type": ["FPGA"]}

        self.PARAMS = {}
        self.INITS = []
        self.STEPS = [
            {
                "mode": "write",
                "var": f"{self.name}_out",
                "bytes": 1,
                "value": setup_value,
            },
        ]
        if self.inputs:
            self.STEPS.append(
                {
                    "mode": "read",
                    "var": f"{self.name}_in",
                    "bytes": 1,
                    "data_in": setup_data_in,
                }
            )

    @classmethod
    def update_prefixes(cls, parent, instances):
        for instance in instances:
            for connected_pin in parent.get_all_plugin_pins(configured=True, prefix=instance.instances_name):
                plugin_instance = connected_pin["instance"]
                if not plugin_instance.PREFIX.startswith(instance.PREFIX):
                    plugin_instance.PREFIX = f"{instance.PREFIX}.{plugin_instance.instances_name}"

    def paint_overlay(self, painter):
        address = int(self.address, 16) - 0x20
        painter.setPen(Qt.GlobalColor.black)
        painter.setBrush(Qt.GlobalColor.yellow)
        for bit in range(3):
            if (1 << bit) & address:
                painter.drawRect(118, 53 - bit * 11, 22, 10)
            else:
                painter.drawRect(129, 53 - bit * 11, 22, 10)
