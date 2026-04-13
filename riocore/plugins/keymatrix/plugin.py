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
            "delay": {
                "default": 1.0,
                "type": float,
                "unit": "ms",
                "min": 0.0,
                "max": 100.0,
                "description": "delay between scans",
            },
            "sendkeys": {
                "default": False,
                "type": bool,
                "description": "using sendkeys hal-component",
            },
            "mapping": {
                "default": "2, 5, 8, 27, 3, 6, 9, 11, 4, 7, 10, 43, 30, 48, 46, 32",
                "type": str,
                "description": "keycodes",
            },
            "bitout": {
                "default": False,
                "type": bool,
                "description": "generate single bit signals",
            },
        }
        cols = self.plugin_setup.get("cols", self.OPTIONS["cols"]["default"])
        rows = self.plugin_setup.get("rows", self.OPTIONS["rows"]["default"])
        self.PINDEFAULTS = {}
        for col in range(cols):
            self.PINDEFAULTS[f"col{col}"] = {
                "direction": "output",
                "pos": (190 + col * 11, 395),
            }
        for row in range(rows):
            self.PINDEFAULTS[f"row{row}"] = {
                "direction": "input",
                "pull": "up",
                "pos": (185 - rows * 11 + row * 11, 395),
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
            "scancode": {
                "direction": "input",
                "hal_type": "u32",
                "interface": "value",
            },
        }
        bitout = self.plugin_setup.get("bitout", self.OPTIONS["bitout"]["default"])
        if bitout:
            for bit in range(cols * rows):
                self.SIGNALS[f"key{bit}"] = {
                    "direction": "input",
                    "bool": True,
                    "interface": "calc",
                }
        self.keysnum = None

    def gateware_instances(self):
        delay = self.plugin_setup.get("delay", self.OPTIONS["delay"]["default"])
        cols = self.plugin_setup.get("cols", self.OPTIONS["cols"]["default"])
        rows = self.plugin_setup.get("rows", self.OPTIONS["rows"]["default"])
        cols_list = []
        rows_list = []
        for col in range(cols - 1, -1, -1):
            cols_list.append(f"PINOUT_{self.instances_name.upper()}_COL{col}")
        for row in range(rows - 1, -1, -1):
            rows_list.append(f"PININ_{self.instances_name.upper()}_ROW{row}")
        instances = self.gateware_instances_base()
        instance = instances[self.instances_name]
        instance_parameter = instance["parameter"]
        divider = int(self.system_setup["speed"] / 1000 / delay)
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

    def convert_c(self, signal_name, signal_setup):
        if signal_name == "scancode":
            return """
    static uint32_t last_value = 0;
    static uint32_t scancode = 0;
    if (value != last_value) {
        if (value == 0) {
            // printf("## up %i \\n", last_value - 1);
            scancode = 0x80 | last_value - 1;
        } else {
            // printf("## down %i \\n", value - 1);
            scancode = 0xC0 | value - 1;
        }
    }
    last_value = value;
    value = scancode;
            """
        if signal_name.startswith("key"):
            bit = int(signal_name[3:])
            signal_prefix = (self.PREFIX or self.title or self.instances_name).replace(" ", "_").replace("<", "-lt-").replace(">", "-gt-").replace(".", "_")
            return f"""
    if (data->VARIN8_{self.instances_name.upper()}_VALUE == {bit + 1}) {{
        *data->SIGIN_{signal_prefix.upper()}_KEY{bit} = 1;
    }} else {{
        *data->SIGIN_{signal_prefix.upper()}_KEY{bit} = 0;
    }}
    *data->SIGIN_{signal_prefix.upper()}_KEY{bit}_not = 1 - *data->SIGIN_{signal_prefix.upper()}_KEY{bit};
            """
        return ""

    @classmethod
    def component_loader(cls, instances):
        keys_list = []
        compnum = 0
        for instance in instances:
            sendkeys = instance.plugin_setup.get("sendkeys", instance.OPTIONS["sendkeys"]["default"])
            if sendkeys:
                cols = instance.plugin_setup.get("cols", instance.OPTIONS["cols"]["default"])
                rows = instance.plugin_setup.get("rows", instance.OPTIONS["rows"]["default"])
                keys_list.append(str(cols * rows))
                instance.keysnum = compnum
                compnum += 1
        if keys_list:
            return f"loadusr -W sendkeys config={','.join(keys_list)}"
        return ""

    def hal(self, parent):
        sendkeys = self.plugin_setup.get("sendkeys", self.OPTIONS["sendkeys"]["default"])
        if not sendkeys or self.keysnum is None:
            return
        signal_prefix = (self.PREFIX or self.instances_name).replace(" ", "_")
        cols = self.plugin_setup.get("cols", self.OPTIONS["cols"]["default"])
        rows = self.plugin_setup.get("rows", self.OPTIONS["rows"]["default"])
        mapping = self.plugin_setup.get("mapping", self.OPTIONS["mapping"]["default"]).replace(",", "").split()
        keys = cols * rows
        parent.halg.net_add(f"{signal_prefix}.scancode", f"sendkeys.{self.keysnum}.keycode", f"scancode{self.keysnum}")
        for key_n in range(keys):
            if key_n < len(mapping):
                parent.halg.setp_add(f"sendkeys.{self.keysnum}.scan-event-{key_n:02d}", mapping[key_n])
        parent.halg.setp_add(f"sendkeys.{self.keysnum}.init", 1)

    def start_sh(self, parent):
        sendkeys = self.plugin_setup.get("sendkeys", self.OPTIONS["sendkeys"]["default"])
        if sendkeys:
            return "sudo modprobe uinput\nsudo chmod 0666 /dev/uinput\n"
