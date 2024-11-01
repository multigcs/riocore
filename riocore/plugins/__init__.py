import time


class Modifiers:
    def pin_modifier_debounce(self, instances, modifier_num, pin_name, pin_varname, modifier, system_setup):
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
        return pin_varname

    def pin_modifier_toggle(self, instances, modifier_num, pin_name, pin_varname, modifier, system_setup):
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
        return pin_varname

    def pin_modifier_invert(self, instances, modifier_num, pin_name, pin_varname, modifier, system_setup):
        instances[f"invert{modifier_num}_{self.instances_name}_{pin_name}"] = {
            "predefines": [
                f"wire {pin_varname}_INVERTED;",
                f"assign {pin_varname}_INVERTED = ~{pin_varname};",
            ],
        }
        pin_varname = f"{pin_varname}_INVERTED"
        return pin_varname

    def pin_modifier_onerror(self, instances, modifier_num, pin_name, pin_varname, modifier, system_setup):
        invert = modifier.get("invert", False)
        invert_char = "~"
        if invert:
            invert_char = ""
        instances[f"onerror{modifier_num}_{self.instances_name}_{pin_name}"] = {
            "predefines": [
                f"wire {pin_varname}_ONERROR;",
                f"assign {pin_varname}_ONERROR = {pin_varname} & {invert_char}ERROR;",
            ],
        }
        pin_varname = f"{pin_varname}_ONERROR"
        return pin_varname

    def pin_modifier_pwm(self, instances, modifier_num, pin_name, pin_varname, modifier, system_setup):
        frequency = modifier.get("frequency", 1)
        dty = modifier.get("dty", 50)
        frequency_divider = system_setup["speed"] // frequency
        dty_divider = frequency_divider * dty // 100
        instances[f"pwm{modifier_num}_{self.instances_name}_{pin_name}"] = {
            "module": "pwmmod",
            "parameter": {"DIVIDER_FREQ": frequency_divider, "DIVIDER_DTY": dty_divider},
            "arguments": {
                "clk": "sysclk",
                "din": pin_varname,
                "dout": f"{pin_varname}_PWM",
            },
        }
        pin_varname = f"{pin_varname}_PWM"
        return pin_varname

    def pin_modifier_list(self, direction=None):
        modifiers = []
        for part in dir(self):
            if part.startswith("pin_modifier_") and part != "pin_modifier_list":
                modifiers.append(part.split("_")[2])
        return modifiers


class PluginBase:
    expansions = []

    def __init__(self, plugin_id, plugin_setup, system_setup=None):
        self.PINDEFAULTS = {}
        self.INTERFACE = {}
        self.SIGNALS = {}
        self.TIMING_CONSTRAINTS = {}
        self.DYNAMIC_SIGNALS = False
        self.VERILOGS = []
        self.NAME = ""
        self.TYPE = "io"
        self.INFO = ""
        self.DESCRIPTION = ""
        self.KEYWORDS = ""
        self.ORIGIN = ""
        self.GATEWARE_SUPPORT = True
        self.FIRMWARE_SUPPORT = False
        self.OPTIONS = {}
        self.PLUGIN_CONFIG = False
        self.LIMITATIONS = {}
        self.system_setup = system_setup
        self.plugin_id = plugin_id
        self.plugin_setup = plugin_setup
        self.setup()

        if self.TYPE == "frameio":
            self.timeout = self.TIMEOUT
            self.delay = self.DELAY
            self.timestamp = time.time() * 1000.0
            self.rxframe_len = 0
            self.rxframe_id = 0
            self.txframe_id_ack = 0
            self.txframe_id = 0
            self.txdata = 0
            self.frame = b""
            self.frame_tx = None
            self.frame_tx_overwride = None

        if "name" not in self.OPTIONS:
            self.OPTIONS["name"] = {
                "type": str,
                "description": "name of this plugin instance",
                "default": "",
            }

        if self.TYPE == "joint":
            if "axis" not in self.OPTIONS:
                self.OPTIONS["axis"] = {
                    "type": "select",
                    "description": "axis name (X,Y,Z,...)",
                    "options": ["X", "Y", "Z", "A", "B", "C", "U", "V", "W"],
                }
            if "is_joint" not in self.OPTIONS:
                self.OPTIONS["is_joint"] = {
                    "type": bool,
                    "default": False,
                    "description": "configure as joint",
                }

        self.update_title()

        if self.TYPE == "expansion":
            expansion_id = len(self.expansions)
            ename = (self.plugin_setup.get("name") or f"EXPANSION{expansion_id}").replace(" ", "_")
            self.expansion_prefix = ename.upper()
            self.expansions.append(self.expansion_prefix)

    def update_title(self):
        self.instances_name = f"{self.NAME}{self.plugin_id}"
        self.title = self.plugin_setup.get("name") or self.instances_name

    def firmware_defines(self):
        return ""

    def firmware_setup(self):
        return ""

    def firmware_loop(self):
        return ""

    def setup(self):
        pass

    def gateware_files(self):
        return self.VERILOGS

    def convert2interface(self):
        if self.TYPE == "frameio":
            frame_ack = False
            frame_timeout = False
            if self.txframe_id_ack == self.txframe_id:
                frame_ack = True
            timestamp = time.time() * 1000.0
            self.time_diff = timestamp - self.timestamp
            if self.time_diff >= self.timeout:
                frame_timeout = True

            if (frame_ack or frame_timeout) and self.time_diff > self.delay:
                self.timestamp = timestamp
                if self.txframe_id < 255:
                    self.txframe_id += 1
                else:
                    self.txframe_id = 0

                txdata = self.frameio_tx(frame_ack, frame_timeout)

                if self.frame_tx_overwride is not None:
                    txdata = self.frame_tx_overwride
                self.frame_tx = txdata

                if txdata is not None:
                    frame_len = len(txdata)
                    data = [0] * (self.plugin_setup.get("tx_buffersize", self.OPTIONS["tx_buffersize"]["default"]) // 8)
                    for n, val in enumerate(txdata):
                        data[n] = val
                    self.frame = bytes([self.txframe_id, frame_len] + data)

            self.INTERFACE["txdata"]["value"] = self.frame
        else:
            interface_data = self.interface_data()
            for signal_name, signal_setup in self.signals().items():
                if signal_setup["direction"] in {"output", "inout"} and signal_name in interface_data:
                    interface_data[signal_name]["value"] = self.convert(signal_name, signal_setup, signal_setup["value"])

    def convert2signals(self):
        if self.TYPE == "frameio":
            self.txframe_id_ack = self.INTERFACE["rxdata"]["value"][0]
            rxframe_id = self.INTERFACE["rxdata"]["value"][1]
            rxframe_len = self.INTERFACE["rxdata"]["value"][2]
            rxframe_new = False
            if rxframe_id != self.rxframe_id:
                rxframe_new = True
            self.rxframe_id = rxframe_id
            self.rxframe_len = rxframe_len
            rxdata = list(reversed(self.INTERFACE["rxdata"]["value"][3 : rxframe_len + 3]))
            self.frameio_rx(rxframe_new, rxframe_id, rxframe_len, rxdata)
        else:
            interface_data = self.interface_data()
            for signal_name, signal_setup in self.signals().items():
                if signal_setup["direction"] == "input" and signal_name in interface_data:
                    signal_setup["value"] = self.convert(signal_name, signal_setup, interface_data[signal_name]["value"])

    def globals_c(self):
        return ""

    def convert(self, signal_name, signal_setup, value):
        return value

    def convert_c(self, signal_name, signal_setup):
        return ""

    def timing_constraints(self):
        return self.TIMING_CONSTRAINTS

    def pins(self):
        pins = {}
        for pin_name, pin_config in self.PINDEFAULTS.items():
            if "pin" in self.plugin_setup and "pins" not in self.plugin_setup:
                print(f"WARNING: old style pin config found ({self.instances_name})")
                self.plugin_setup["pins"] = {pin_name: {"pin": self.plugin_setup["pin"]}}

            if "pins" not in self.plugin_setup:
                # print(f"WARNING: no pins found in config ({self.instances_name})")
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
                # exit(1)
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
            signal_prefix = (self.plugin_setup.get("name") or self.instances_name).replace(" ", "_")
            halname = f"{signal_prefix}.{name}"
            direction_short = setup["direction"].upper().replace("PUT", "")
            signals[name]["signal_prefix"] = signal_prefix
            signals[name]["var_prefix"] = signal_prefix.replace(".", "_").replace("-", "_").upper()
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

            multiplexed = self.plugin_setup.get("multiplexed")
            if multiplexed is not None:
                data[name]["multiplexed"] = multiplexed

            data[name]["variable"] = f"VAR{direction}{size}_{self.instances_name}_{name}".upper()
        return data

    def expansion_outputs(self):
        expansion_pins = []
        if self.TYPE == "expansion":
            bits = self.plugin_setup.get("bits", 8)
            for num in range(0, bits):
                expansion_pins.append(f"{self.expansion_prefix}_OUTPUT[{num}]")
        return expansion_pins

    def expansion_inputs(self):
        expansion_pins = []
        if self.TYPE == "expansion":
            bits = self.plugin_setup.get("bits", 8)
            for num in range(0, bits):
                expansion_pins.append(f"{self.expansion_prefix}_INPUT[{num}]")
        return expansion_pins

    def gateware_defines(self, direct=False):
        defines = []
        if self.TYPE == "expansion":
            bits = self.plugin_setup.get("bits", 8)
            defines.append(f"wire [{bits-1}:0] {self.expansion_prefix}_INPUT;")
            defines.append(f"wire [{bits-1}:0] {self.expansion_prefix}_OUTPUT;")
        return defines

    def gateware_pin_modifiers(self, instances, instance, pin_name, pin_config, pin_varname):
        instance_predefines = instance["predefines"]
        direction = pin_config["direction"]
        modifier_list = pin_config.get("modifier", [])
        pin_varname_org = pin_varname
        if direction == "output":
            instance_predefines.append(f"wire {pin_varname_org}_RAW;")
            pin_varname = f"{pin_varname_org}_RAW"
        for modifier_num, modifier in enumerate(modifier_list):
            if modifier:
                modifier_type = modifier["type"]
                modifier_function = getattr(Modifiers, f"pin_modifier_{modifier_type}")
                if modifier_function:
                    pin_varname = modifier_function(self, instances, modifier_num, pin_name, pin_varname, modifier, self.system_setup)
        if direction == "output":
            instances[f"{self.instances_name}_{pin_name}_RAW"] = {
                "predefines": [
                    f"assign {pin_varname_org} = {pin_varname};",
                ],
            }
            pin_varname = f"{pin_varname_org}_RAW"
        return pin_varname

    def gateware_instances_base(self, direct=False):
        instances = {}
        instance = {"module": self.NAME, "direct": direct, "parameter": {}, "arguments": {}, "predefines": []}
        instance_predefines = instance["predefines"]
        instance_arguments = instance["arguments"]
        pin_varname = None

        if direct is False:
            instance_arguments["clk"] = "sysclk"
        for pin_name, pin_config in self.pins().items():
            pin_varname = pin_config["varname"]
            if "pin" in pin_config:
                pin_varname = self.gateware_pin_modifiers(instances, instance, pin_name, pin_config, pin_varname)
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

        elif self.TYPE == "expansion":
            instance_arguments["data_in"] = f"{self.expansion_prefix}_INPUT"
            instance_arguments["data_out"] = f"{self.expansion_prefix}_OUTPUT"

        elif direct is True and pin_varname is not None:
            for interface_name, interface_setup in self.interface_data().items():
                if interface_setup["direction"] in {"output", "inout"}:
                    instance_predefines.append(f"assign {pin_varname} = {interface_setup['variable']};")
                else:
                    instance_predefines.append(f"assign {interface_setup['variable']} = {pin_varname};")

        instances[self.instances_name] = instance
        return instances

    def gateware_instances(self):
        instances = self.gateware_instances_base()
        return instances

    def option_default(self, name, default=None):
        return self.OPTIONS.get(name, {}).get("default", default)

    def basic_config(self):
        basic_config = {
            "type": self.NAME,
            "pins": {},
        }
        pn = 0
        for pin_name, pin_setup in self.PINDEFAULTS.items():
            default = pin_setup.get("default")
            if default is not None:
                basic_config["pins"][pin_name] = {"pin": f"{default}"}
            else:
                basic_config["pins"][pin_name] = {"pin": f"{pn}"}
            pn += 1
        return basic_config

    def full_config(self):
        full_config = {
            "type": self.NAME,
        }

        for option_name, option_setup in self.OPTIONS.items():
            default = ""
            if option_setup["type"] is int:
                default = 0
            elif option_setup["type"] is float:
                default = 0.0
            elif option_setup["type"] is bool:
                default = False
            full_config[option_name] = option_setup.get("default", default)

        pn = 0
        full_config["pins"] = {}
        for pin_name, pin_setup in self.PINDEFAULTS.items():
            default = pin_setup.get("default")
            if default is not None:
                full_config["pins"][pin_name] = {"pin": f"{default}", "modifiers": []}
            else:
                full_config["pins"][pin_name] = {"pin": f"{pn}", "modifiers": []}
            if pin_setup["direction"] == "input":
                full_config["pins"][pin_name]["modifiers"].append({"type": "debounce"})
                if pn > 0:
                    full_config["pins"][pin_name]["modifiers"].append({"type": "invert"})
            else:
                full_config["pins"][pin_name]["modifiers"].append({"type": "invert"})
            pn += 1

        full_config["signals"] = {}
        for signal_name, signal_setup in self.SIGNALS.items():
            full_config["signals"][signal_name] = {
                "net": "xxx.yyy.zzz",
                "function": "rio.xxx",
            }
            if signal_setup.get("bool", False) is False:
                full_config["signals"][signal_name]["scale"] = 100.0
                full_config["signals"][signal_name]["offset"] = 0.0

            full_config["signals"][signal_name]["display"] = {
                "title": signal_name,
                "section": "status",
                "type": "meter",
            }

            if signal_setup["direction"] == "input":
                full_config["signals"][signal_name]["display"]["section"] = "inputs"
                if signal_setup.get("bool", False) is True:
                    full_config["signals"][signal_name]["display"]["type"] = "led"
            elif signal_setup["direction"] == "output":
                full_config["signals"][signal_name]["display"]["section"] = "outputs"
                if signal_setup.get("bool", False) is True:
                    full_config["signals"][signal_name]["display"]["type"] = "checkbox"
                else:
                    full_config["signals"][signal_name]["display"]["type"] = "scale"

        return full_config

    def show_pins(self):
        output = []
        for pin_name, pin_setup in self.PINDEFAULTS.items():
            direction = pin_setup.get("direction")
            pull = pin_setup.get("pull")
            description = pin_setup.get("description")
            default = pin_setup.get("default")
            optional = pin_setup.get("optional")

            output.append(f"### {pin_name}:")
            if description:
                output.append(description)
            output.append("")

            output.append(f" * direction: {direction}")
            if pull is not None:
                output.append(f" * pull: {pull}")
            if default is not None:
                output.append(f" * default: {default}")
            if optional is not None:
                output.append(f" * optional: {optional}")

            output.append("")
        return "\n".join(output)

    def show_options(self):
        output = []
        for option_name, option_setup in self.OPTIONS.items():
            vtype = option_setup.get("type")
            description = option_setup.get("description")
            vmin = option_setup.get("min")
            vmax = option_setup.get("max")
            unit = option_setup.get("unit")
            if not isinstance(vtype, str):
                vtype = vtype.__name__

            output.append(f"### {option_name}:")
            if description:
                output.append(description)
            output.append("")

            output.append(f" * type: {vtype}")
            if vmin is not None:
                output.append(f" * min: {vmin}")
            if vmax is not None:
                output.append(f" * max: {vmax}")
            output.append(f" * default: {option_setup.get('default')}")
            if unit is not None:
                output.append(f" * unit: {unit}")

            output.append("")
        return "\n".join(output)

    def show_signals(self):
        output = []
        if self.DYNAMIC_SIGNALS:
            output.append("the signals of this plugin are user configurable")
            output.append("")
        else:
            for signal_name, signal_setup in self.SIGNALS.items():
                isbool = signal_setup.get("bool", False)
                direction = signal_setup.get("direction")
                description = signal_setup.get("description")
                vmin = signal_setup.get("min")
                vmax = signal_setup.get("max")
                unit = signal_setup.get("unit")
                output.append(f"### {signal_name}:")
                if description:
                    output.append(description)
                output.append("")

                if isbool:
                    output.append(" * type: bit")
                else:
                    output.append(" * type: float")
                output.append(f" * direction: {direction}")
                if vmin is not None:
                    output.append(f" * min: {vmin}")
                if vmax is not None:
                    output.append(f" * max: {vmax}")

                if unit is not None:
                    output.append(f" * unit: {unit}")

                output.append("")

        return "\n".join(output)

    def show_interfaces(self):
        output = []
        for interface_name, interface_setup in self.INTERFACE.items():
            size = interface_setup.get("size")
            direction = interface_setup.get("direction")
            description = interface_setup.get("description")
            multiplexed = interface_setup.get("multiplexed")

            output.append(f"### {interface_name}:")
            if description:
                output.append(description)
            output.append("")

            output.append(f" * size: {size} bit")
            output.append(f" * direction: {direction}")
            if multiplexed:
                output.append(f" * multiplexed: {multiplexed}")

            output.append("")
        return "\n".join(output)
