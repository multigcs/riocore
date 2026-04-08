from riocore.plugins import PluginBase


class Plugin(PluginBase):
    def setup(self):
        self.NAME = "keymatrix"
        self.INFO = "Matix-Keyboard"
        self.DESCRIPTION = "input for matrix keyboards"
        self.KEYWORDS = "keyboard keys"
        self.ORIGIN = ""
        self.NEEDS = ["fpga"]
        self.VERILOGS = ["keymatrix.v"]
        self.IMAGE_SHOW = True
        self.OPTIONS = {
            "cols": {
                "default": 4,
                "type": int,
                "min": 0,
                "max": 8,
                "description": "number cols",
            },
            "rows": {
                "default": 4,
                "type": int,
                "min": 0,
                "max": 8,
                "description": "number rows",
            },
        }
        cols = self.plugin_setup.get("cols", 4)
        rows = self.plugin_setup.get("rows", 4)
        self.PINDEFAULTS = {}
        for col in range(cols):
            self.PINDEFAULTS[f"col{col}"] = {
                "direction": "output",
                "pos": (185 - cols * 11 + col * 11, 395),
            }
        for row in range(rows):
            self.PINDEFAULTS[f"row{row}"] = {
                "direction": "input",
                "pull": "up",
                "pos": (190 + row * 11, 395),
            }
        self.INTERFACE = {
            "value": {
                "size": 8,
                "direction": "input",
            },
        }
        self.SIGNALS = {
            "value": {
                "direction": "input",
            },
        }

    def gateware_instances(self):
        cols = self.plugin_setup.get("cols", 4)
        rows = self.plugin_setup.get("rows", 4)
        cols_list = []
        rows_list = []
        for col in range(cols):
            cols_list.append(f"PINOUT_{self.instances_name.upper()}_COL{col}")
        for row in range(rows):
            rows_list.append(f"PININ_{self.instances_name.upper()}_ROW{row}")
        instances = self.gateware_instances_base()
        instance = instances[self.instances_name]
        instance_parameter = instance["parameter"]
        divider = self.system_setup["speed"] // 1000 // 2
        instance_parameter["DIVIDER"] = divider
        instance_parameter["ROWS"] = rows
        instance_parameter["COLS"] = cols
        instance_parameter["VALUE_BITS"] = self.clog2(rows * cols + 1)
        for key in list(instance["arguments"]):
            if key in {"clk", "value"}:
                continue
            del instance["arguments"][key]
        instance["arguments"]["cols"] = f"{{{', '.join(cols_list)}}}"
        instance["arguments"]["rows"] = f"{{{', '.join(rows_list)}}}"
        return instances
