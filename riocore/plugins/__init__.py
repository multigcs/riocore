class PluginBase:
    expansions = []

    def __init__(self, plugin_id, plugin_setup, system_setup=None):
        self.PINDEFAULTS = {}
        self.INTERFACE = {}
        self.SIGNALS = {}
        self.VERILOGS = []
        self.NAME = ""
        self.TYPE = "io"
        self.INFO = ""
        self.DESCRIPTION = ""
        self.OPTIONS = {}
        self.system_setup = system_setup
        self.plugin_id = plugin_id
        self.plugin_setup = plugin_setup
        self.setup()

        if "name" not in self.OPTIONS:
            self.OPTIONS["name"] = {
                "type": str,
            }

        if self.INTERFACE and "net" not in self.OPTIONS:
            self.OPTIONS["net"] = {
                "type": str,
            }

        if self.TYPE == "joint" and "scale" not in self.OPTIONS:
            self.OPTIONS["scale"] = {
                "type": float,
            }

        self.instances_name = f"{self.NAME}{self.plugin_id}"
        self.title = plugin_setup.get("name") or self.instances_name

        if self.TYPE == "expansion":
            expansion_id = len(self.expansions)
            self.expansion_prefix = self.plugin_setup.get("name", f"EXPANSION{expansion_id}")
            self.expansions.append(self.expansion_prefix)

    def setup(self):
        pass

    def gateware_files(self):
        return self.VERILOGS

    def convert2interface(self):
        interface_data = self.interface_data()
        for signal_name, signal_setup in self.signals().items():
            if signal_setup["direction"] == "output" and signal_name in interface_data:
                interface_data[signal_name]["value"] = self.convert(signal_name, signal_setup, signal_setup["value"])

    def convert2signals(self):
        interface_data = self.interface_data()
        for signal_name, signal_setup in self.signals().items():
            if signal_setup["direction"] == "input" and signal_name in interface_data:
                signal_setup["value"] = self.convert(signal_name, signal_setup, interface_data[signal_name]["value"])

    def convert(self, signal_name, signal_setup, value):
        return value

    def pins(self):
        pins = {}
        for pin_name, pin_config in self.PINDEFAULTS.items():
            if "pin" in self.plugin_setup and "pins" not in self.plugin_setup:
                print(f"WARNING: old style pin config found ({self.instances_name})")
                self.plugin_setup["pins"] = {pin_name: {"pin": self.plugin_setup["pin"]}}

            if "pins" not in self.plugin_setup:
                print(f"WARNING: no pins found in config ({self.instances_name})")
                continue

            if pin_name.upper() in self.plugin_setup["pins"]:
                print(f"WARNING: please use lowercase for pinnames: {pin_name} ({self.instances_name})")
                self.plugin_setup["pins"][pin_name] = self.plugin_setup["pins"][pin_name.upper()]

            if pin_name in self.plugin_setup["pins"]:
                pins[pin_name] = pin_config.copy()
                for pincfg in pins[pin_name]:
                    if isinstance(self.plugin_setup["pins"][pin_name], str):
                        print(f"WARNING: please use dict for the pin setup: {self.plugin_setup['pins'][pin_name]}")
                        self.plugin_setup["pins"][pin_name] = {"pin": self.plugin_setup["pins"][pin_name]}
                        print(f"WARNING: -> {self.plugin_setup['pins'][pin_name]}")
                        print("")
                pins[pin_name].update(self.plugin_setup["pins"][pin_name])
                direction = pin_config["direction"].upper().replace("PUT", "")
                pins[pin_name]["varname"] = f"PIN{direction}_{self.instances_name}_{pin_name}".upper()
            elif pin_config.get("optional") is not True:
                print(f"ERROR: MISSING PIN CONFIGURATION for '{pin_name}' ({self.NAME})")
                exit(1)
            else:
                pins[pin_name] = pin_config.copy()
                pins[pin_name]["varname"] = f"UNUSED_PIN_{self.instances_name}_{pin_name}".upper()
        return pins

    def signals(self):
        signals = {}
        for name, setup in self.SIGNALS.items():
            if "value" not in setup:
                setup["value"] = 0
            signals[name] = setup
            for key in setup:
                if key in self.plugin_setup:
                    setup[key] = self.plugin_setup[key]
            signal_prefix = self.plugin_setup.get("name", self.instances_name)
            halname = f"{signal_prefix}.{name}"
            direction_short = setup["direction"].upper().replace("PUT", "")
            signals[name]["plugin_instance"] = self
            signals[name]["halname"] = halname
            signals[name]["varname"] = f"SIG{direction_short}_{halname.replace('.', '_').replace('-', '_').upper()}"
            signals[name]["userconfig"] = self.plugin_setup.get("signals", {}).get(name, {})
            net = self.plugin_setup.get("net")
            netname = net
            if len(self.SIGNALS) > 1 and net:
                netname = f"{net}.{name}"
            signals[name]["netname"] = signals[name]["userconfig"].get("net", netname)
        return signals

    def interface_data(self):
        data = {}
        for name, setup in self.INTERFACE.items():
            if "value" not in setup:
                setup["value"] = 0
            size = setup.get("size", 32)
            direction = setup["direction"].upper().replace("PUT", "")
            data[name] = setup
            data[name]["variable"] = f"VAR{direction}{size}_{self.instances_name}_{name}".upper()
        return data

    def gateware_defines(self, direct=False):
        defines = []
        if self.TYPE == "expansion":
            bits = self.plugin_setup.get("bits", 8)
            defines.append(f"wire [{bits-1}:0] {self.expansion_prefix}_INPUT;")
            defines.append(f"wire [{bits-1}:0] {self.expansion_prefix}_OUTPUT;")
        return defines

    def gateware_pin_modifier(self, instances, instance, pin_name, pin_config, pin_varname):
        instance_predefines = instance["predefines"]
        instance_arguments = instance["arguments"]

        if pin_config["direction"] == "input":
            for modifier_num, modifier in enumerate(pin_config.get("modifier", [])):
                if modifier:
                    modifier_type = modifier["type"]
                    if modifier_type == "debounce":
                        width = modifier.get("delay", 16)
                        instances[f"debouncer{modifier_num}_{self.instances_name}_{pin_name}"] = {
                            "module": "debouncer",
                            "parameter": {"WIDTH": width},
                            "arguments": {
                                "clk": "sysclk",
                                "din": pin_varname,
                                "dout": f"{pin_varname}_DEBOUNCED",
                            },
                            "predefines": [f"wire {pin_varname}_DEBOUNCED;"],
                        }
                        pin_varname = f"{pin_varname}_DEBOUNCED"

                    if modifier_type == "toggle":
                        instances[f"toggle{modifier_num}_{self.instances_name}_{pin_name}"] = {
                            "module": "toggle",
                            "arguments": {
                                "clk": "sysclk",
                                "din": pin_varname,
                                "dout": f"{pin_varname}_TOGGLED",
                            },
                            "predefines": [f"wire {pin_varname}_TOGGLED;"],
                        }
                        pin_varname = f"{pin_varname}_TOGGLED"

                    if modifier_type == "invert":
                        instances[f"invert{modifier_num}_{self.instances_name}_{pin_name}"] = {
                            "predefines": [
                                f"wire {pin_varname}_INVERTED;",
                                f"assign {pin_varname}_INVERTED = ~{pin_varname};",
                            ],
                        }
                        pin_varname = f"{pin_varname}_INVERTED"

                    if modifier_type == "onerror":
                        instances[f"onerror{modifier_num}_{self.instances_name}_{pin_name}"] = {
                            "predefines": [
                                f"wire {pin_varname}_ONERROR;",
                                f"assign {pin_varname}_ONERROR = {pin_varname} & ~ERROR;",
                            ],
                        }
                        pin_varname = f"{pin_varname}_ONERROR"

        elif pin_config["direction"] == "output":
            for modifier_num, modifier in enumerate(reversed(pin_config.get("modifier", []))):
                if modifier:
                    modifier_type = modifier["type"]
                    if modifier_type == "debounce":
                        width = modifier.get("delay", 16)
                        instances[f"debouncer{modifier_num}_{self.instances_name}_{pin_name}"] = {
                            "module": "debouncer",
                            "parameter": {"WIDTH": width},
                            "arguments": {
                                "clk": "sysclk",
                                "din": f"{pin_varname}_DEBOUNCE",
                                "dout": pin_varname,
                            },
                            "predefines": [f"wire {pin_varname}_DEBOUNCE;"],
                        }
                        pin_varname = f"{pin_varname}_DEBOUNCE"

                    if modifier_type == "toggle":
                        instances[f"toggle{modifier_num}_{self.instances_name}_{pin_name}"] = {
                            "module": "toggle",
                            "arguments": {
                                "clk": "sysclk",
                                "din": f"{pin_varname}_TOGGLE",
                                "dout": pin_varname,
                            },
                            "predefines": [f"wire {pin_varname}_TOGGLE;"],
                        }
                        pin_varname = f"{pin_varname}_TOGGLE"

                    if modifier_type == "invert":
                        instances[f"invert{modifier_num}_{self.instances_name}_{pin_name}"] = {
                            "predefines": [
                                f"wire {pin_varname}_INVERT;",
                                f"assign {pin_varname} = ~{pin_varname}_INVERT;",
                            ],
                        }
                        pin_varname = f"{pin_varname}_INVERT"

                    if modifier_type == "onerror":
                        instances[f"onerror{modifier_num}_{self.instances_name}_{pin_name}"] = {
                            "predefines": [
                                f"wire {pin_varname}_ONERROR;",
                                f"assign {pin_varname} = {pin_varname}_ONERROR & ~ERROR;",
                            ],
                        }
                        pin_varname = f"{pin_varname}_ONERROR"

        return pin_varname

    def gateware_instances_base(self, direct=False):
        instances = {}
        instance = {"module": self.NAME, "direct": direct, "parameter": {}, "arguments": {}, "predefines": []}
        instance_predefines = instance["predefines"]
        instance_arguments = instance["arguments"]

        if direct is False:
            instance_arguments["clk"] = "sysclk"
        for pin_name, pin_config in self.pins().items():
            pin_varname = pin_config["varname"]
            if "pin" in pin_config:

                pin_varname = self.gateware_pin_modifier(instances, instance, pin_name, pin_config, pin_varname)
                instance_arguments[pin_name] = pin_varname

            elif pin_config["direction"] == "input":
                instance_arguments[pin_name] = pin_config.get("default", "1'd0")
            else:
                instance_arguments[pin_name] = pin_varname
                instance_predefines.append(f"wire {pin_varname};")

        if direct is False:
            for interface_name, interface_setup in self.interface_data().items():
                on_error = interface_setup.get("on_error")
                if on_error is False:
                    instance_arguments[interface_name] = f"{interface_setup['variable']} & ~ERROR"
                elif on_error is True:
                    instance_arguments[interface_name] = f"{interface_setup['variable']} | ERROR"
                else:
                    instance_arguments[interface_name] = interface_setup["variable"]

        if self.TYPE == "interface":
            instance_arguments["rx_data"] = "rx_data"
            instance_arguments["tx_data"] = "tx_data"
            instance_arguments["sync"] = "INTERFACE_SYNC"
            instance_arguments["pkg_timeout"] = "INTERFACE_TIMEOUT"

        elif self.TYPE == "expansion":
            instance_arguments["data_in"] = f"{self.expansion_prefix}_INPUT"
            instance_arguments["data_out"] = f"{self.expansion_prefix}_OUTPUT"

        elif direct is True:
            for interface_name, interface_setup in self.interface_data().items():
                if interface_setup["direction"] == "output":
                    instance_predefines.append(f"assign {pin_varname} = {interface_setup['variable']};")
                else:
                    instance_predefines.append(f"assign {interface_setup['variable']} = {pin_varname};")

        instances[self.instances_name] = instance
        return instances

    def gateware_instances(self):
        instances = self.gateware_instances_base()
        return instances

    def convert_c(self, signal_name, signal_setup):
        return ""

    def basic_config(self):
        basic_config = {
            "type": self.NAME,
            "pins": {},
        }
        pn = 0
        for pin_name, pin_setup in self.PINDEFAULTS.items():
            basic_config["pins"][pin_name] = {"pin": f"{pn}"}
            pn += 1
        return basic_config
