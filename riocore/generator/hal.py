#!/usr/bin/env python3
#
# hal generator: can resolve logic operation, multiple assignments and invert pins
#

from riocore import halpins


class hal_generator:
    POSTGUI_COMPONENTS = [
        "pyvcp",
        "gladevcp",
        "rio-gui",
        "qtdragon",
        "qtvcp",
        "qtpyvcp",
        "axisui",
        "mpg",
        "vismach",
        "kinstype",
        "melfagui",
        "fanuc_200f",
        "gmoccapy",
        "flexhal",
        "hal_manualtoolchange",
    ]
    VIRTUAL_COMPONENTS = [
        "riov",
    ]
    HAS_INVERTS = {"rio": "-not"}

    def __init__(self, halpin_info=None):
        self.halpin_info = halpin_info or {}
        self.logic_ids = {}
        self.signals_out = {}
        self.inputs2signals = {}
        self.outputs2signals = {}
        self.function_cache = {}
        self.hal_logics = {}
        self.hal_calcs = {}
        self.setps = {}
        self.preformated = []
        self.preformated_top = []

    def postgui_components_add(self, component):
        self.POSTGUI_COMPONENTS.append(component)

    def virtual_components_add(self, component):
        self.POSTGUI_COMPONENTS.append(component)

    def pin2signal(self, pin, target, signal_name=None):
        if pin.startswith("sig:"):
            return pin.split(":", 2)[-1]
        elif signal_name:
            if pin in self.inputs2signals:
                if self.inputs2signals[pin]["signal"] != signal_name:
                    print(pin, target)
                    print(f"ERROR: pin ({pin}) already exist as signal: {self.inputs2signals[pin]['signal']} (!= {signal_name})")
                    signal = self.inputs2signals[pin]["signal"]
                else:
                    signal = signal_name
            elif pin in self.outputs2signals:
                signal = self.outputs2signals[pin]["signals"][0]
            else:
                signal = signal_name
                self.inputs2signals[pin] = {"signal": signal, "target": target}
        elif pin not in self.inputs2signals:
            if pin in self.outputs2signals:
                signal = self.outputs2signals[pin]["signals"][0]
            else:
                if pin.startswith("func."):
                    signal = f"{pin.replace('.', '_')}"
                else:
                    signal = f"sig_{pin.replace('.', '_')}"
                self.inputs2signals[pin] = {"signal": signal, "target": target}
        else:
            signal = self.inputs2signals[pin]["signal"]
        return signal

    def logic2signal(self, expression, target):
        logic_types = {"AND": 0x100, "OR": 0x200, "XOR": 0x400, "NAND": 0x800, "NOR": 0x1000}
        int_types = {"S+": "scaled_s32_sums", "+": "sum2", "-": "sum2", "*": "mult2", "/": "div2"}
        wcomp_types = {"<": "under", ">": "over", "<=": "under", ">=": "over", "<>": "out"}
        # TODO; using comp for lower / grater

        if expression in self.function_cache:
            return self.function_cache[expression]

        if target not in self.logic_ids:
            self.logic_ids[target] = 0
        self.logic_ids[target] += 1
        logic_num = list(self.logic_ids).index(target)
        new_signal = f"{logic_num}.{self.logic_ids[target]}"
        parts = expression.split()
        n_inputs = (len(parts) + 1) // 2
        etype = parts[1].upper()
        if etype in logic_types:
            # pin1 AND pin2
            # pin1 OR pin2
            personality = logic_types[etype] + n_inputs
            fname = f"func.{etype.lower()}_{new_signal}"
            self.hal_logics[fname] = f"0x{personality:x}"
            for in_n in range(n_inputs):
                input_pin = parts[in_n * 2]
                if input_pin.replace(".", "").lstrip("-").isnumeric():
                    self.setp_add(f"{fname}.in-{in_n:02d}", input_pin)
                    continue
                if input_pin[0] == "!":
                    input_pin = self.pin_not(input_pin[1:], target)
                input_signal = self.pin2signal(input_pin, target)
                if f"{fname}.in-{in_n:02d}" not in self.outputs2signals:
                    self.outputs2signals[f"{fname}.in-{in_n:02d}"] = {"signals": [input_signal], "target": target}
                else:
                    self.outputs2signals[f"{fname}.in-{in_n:02d}"]["signals"].append(input_signal)
            output_pin = f"{fname}.{etype.lower()}"

        elif etype in wcomp_types:
            # pin > value
            # pin <= value
            # pin <> value1,value2
            wcomp_out = wcomp_types[etype]
            fname = f"func.wcomp_{wcomp_out}_{new_signal}"
            if "wcomp" not in self.hal_calcs:
                self.hal_calcs["wcomp"] = []
            self.hal_calcs["wcomp"].append(fname)
            input_pin = parts[0]
            min_value = parts[2]
            max_value = min_value
            if etype == ">":
                if min_value.replace(".", "").isnumeric():
                    max_value = str(float(min_value) + 0.001)
            elif etype == "<":
                if min_value.replace(".", "").isnumeric():
                    min_value = str(float(min_value) - 0.001)
            elif etype == "<>":
                if "," in min_value:
                    max_value = min_value.split(",")[1]
                    min_value = min_value.split(",")[0]
                else:
                    max_value = min_value
            input_signal = self.pin2signal(input_pin, target)
            if f"{fname}.in" not in self.outputs2signals:
                self.outputs2signals[f"{fname}.in"] = {"signals": [input_signal], "target": target}
            else:
                self.outputs2signals[f"{fname}.in"]["signals"].append(input_signal)
            if min_value.replace(".", "").isnumeric():
                self.setp_add(f"{fname}.min", min_value)
            else:
                input_signal = self.pin2signal(min_value, target)
                if f"{fname}.min" not in self.outputs2signals:
                    self.outputs2signals[f"{fname}.min"] = {"signals": [input_signal], "target": target}
                else:
                    self.outputs2signals[f"{fname}.min"]["signals"].append(input_signal)
            if max_value.replace(".", "").isnumeric():
                self.setp_add(f"{fname}.max", max_value)
            else:
                input_signal = self.pin2signal(max_value, target)
                if f"{fname}.max" not in self.outputs2signals:
                    self.outputs2signals[f"{fname}.max"] = {"signals": [input_signal], "target": target}
                else:
                    self.outputs2signals[f"{fname}.max"]["signals"].append(input_signal)

            output_pin = f"{fname}.{wcomp_out}"

        else:
            # pin1 * pin2
            # pin1 / pin2
            personality = int_types[etype]
            if etype == "-":
                fname = f"func.sub2_{new_signal}"
            else:
                fname = f"func.{int_types[etype]}_{new_signal}"
            if personality not in self.hal_calcs:
                self.hal_calcs[personality] = []
            self.hal_calcs[personality].append(fname)
            for in_n in range(n_inputs):
                input_pin = parts[in_n * 2]
                if input_pin.replace(".", "").lstrip("-").isnumeric():
                    self.setp_add(f"{fname}.in{in_n}", input_pin)
                    continue
                input_signal = self.pin2signal(input_pin, target)
                if f"{fname}.in{in_n}" not in self.outputs2signals:
                    self.outputs2signals[f"{fname}.in{in_n}"] = {"signals": [input_signal], "target": target}
                else:
                    self.outputs2signals[f"{fname}.in{in_n}"]["signals"].append(input_signal)

                if etype == "-" and in_n == 1:
                    self.outputs2signals[f"{fname}.gain{in_n}"] = {"signals": -1, "target": target}

            if etype.upper() == "S+":
                output_pin = f"{fname}.out-s"
            else:
                output_pin = f"{fname}.out"

        self.function_cache[expression] = output_pin
        return output_pin

    def text_in_bracket(self, text, right):
        chars = []
        b_end = False
        for c in reversed(text[:right]):
            if b_end and c not in {" ", ")", "("}:
                chars.append(c)
            elif b_end:
                break
            elif c == "(":
                b_end = True
                chars.append(c)
            else:
                chars.append(c)
        return "".join(reversed(chars))

    def pin_not(self, input_pin, target):
        component = input_pin.split(".", 1)[0]
        if component in self.HAS_INVERTS:
            return f"{input_pin}{self.HAS_INVERTS[component]}"
        if input_pin in self.HAS_INVERTS:
            return f"{input_pin}{self.HAS_INVERTS[input_pin]}"
        if target not in self.logic_ids:
            self.logic_ids[target] = 0
        self.logic_ids[target] += 1
        fname = f"func.not_{input_pin.replace('.', '_')}"
        if fname in self.function_cache:
            return self.function_cache[fname]
        if "not" not in self.hal_calcs:
            self.hal_calcs["not"] = []
        self.hal_calcs["not"].append(fname)

        input_signal = self.pin2signal(input_pin, target)
        self.outputs2signals[f"{fname}.in"] = {"signals": [input_signal], "target": target}
        self.function_cache[fname] = f"{fname}.out"
        return f"{fname}.out"

    def pin_abs(self, input_pin, target):
        if target not in self.logic_ids:
            self.logic_ids[target] = 0
        self.logic_ids[target] += 1
        fname = f"func.abs_{input_pin.replace('.', '_')}"
        if fname in self.function_cache:
            return self.function_cache[fname]
        if "abs" not in self.hal_calcs:
            self.hal_calcs["abs"] = []
        self.hal_calcs["abs"].append(fname)
        input_signal = self.pin2signal(input_pin, target)
        self.outputs2signals[f"{fname}.in"] = {"signals": [input_signal], "target": target}
        self.function_cache[fname] = f"{fname}.out"
        return f"{fname}.out"

    def pin_delay(self, input_pin, target, on, off):
        if target not in self.logic_ids:
            self.logic_ids[target] = 0
        self.logic_ids[target] += 1
        if "timedelay" not in self.hal_calcs:
            self.hal_calcs["timedelay"] = []
        fnum = len(self.hal_calcs["timedelay"]) + 1
        fname = f"func.timedelay-{fnum}"
        if fname in self.function_cache:
            return self.function_cache[fname]
        self.hal_calcs["timedelay"].append(fname)
        input_signal = self.pin2signal(input_pin, target)
        self.outputs2signals[f"{fname}.in"] = {"signals": [input_signal], "target": target}
        self.setp_add(f"{fname}.on-delay", on)
        self.setp_add(f"{fname}.off-delay", off)
        self.function_cache[fname] = f"{fname}.out"
        return f"{fname}.out"

    def pin_limit(self, input_pin, target, lmin, lmax):
        if target not in self.logic_ids:
            self.logic_ids[target] = 0
        self.logic_ids[target] += 1
        if "limit1" not in self.hal_calcs:
            self.hal_calcs["limit1"] = []
        fnum = len(self.hal_calcs["limit1"]) + 1
        fname = f"func.limit1-{fnum}"
        if fname in self.function_cache:
            return self.function_cache[fname]
        self.hal_calcs["limit1"].append(fname)
        input_signal = self.pin2signal(input_pin, target)
        self.outputs2signals[f"{fname}.in"] = {"signals": [input_signal], "target": target}
        self.setp_add(f"{fname}.min", lmin)
        self.setp_add(f"{fname}.max", lmax)
        self.function_cache[fname] = f"{fname}.out"
        return f"{fname}.out"

    def pin_deadzone(self, input_pin, target, center, threshold):
        if target not in self.logic_ids:
            self.logic_ids[target] = 0
        self.logic_ids[target] += 1
        if "deadzone" not in self.hal_calcs:
            self.hal_calcs["deadzone"] = []
        fnum = len(self.hal_calcs["deadzone"]) + 1
        fname = f"func.deadzone-{fnum}"
        if fname in self.function_cache:
            return self.function_cache[fname]
        self.hal_calcs["deadzone"].append(fname)
        input_signal = self.pin2signal(input_pin, target)
        self.outputs2signals[f"{fname}.in"] = {"signals": [input_signal], "target": target}
        self.setp_add(f"{fname}.center", center)
        self.setp_add(f"{fname}.threshold", threshold)
        self.function_cache[fname] = f"{fname}.out"
        return f"{fname}.out"

    def pin_chargepump(self, divider):
        if divider:
            input_pin = f"charge-pump.out-{divider}"
        else:
            input_pin = "charge-pump.out"
        self.hal_calcs["charge_pump"] = ["charge-pump"]
        return input_pin

    def pin_conv(self, input_pin, target, type_in, type_out):
        if target not in self.logic_ids:
            self.logic_ids[target] = 0
        self.logic_ids[target] += 1
        func = f"conv_{type_in}_{type_out}"
        if func not in {
            "conv_bit_float",
            "conv_bit_s32",
            "conv_bit_u32",
            "conv_float_s32",
            "conv_float_u32",
            "conv_s32_bit",
            "conv_s32_float",
            "conv_s32_u32",
            "conv_u32_bit",
            "conv_u32_float",
            "conv_u32_s32",
        }:
            print(f"component: {func} not found")
            exit(1)

        if func not in self.hal_calcs:
            self.hal_calcs[func] = []
        fnum = len(self.hal_calcs[func]) + 1
        fname = f"func.{func}-{fnum}"
        if fname in self.function_cache:
            return self.function_cache[fname]
        self.hal_calcs[func].append(fname)
        input_signal = self.pin2signal(input_pin, target)
        self.outputs2signals[f"{fname}.in"] = {"signals": [input_signal], "target": target}
        self.function_cache[fname] = f"{fname}.out"
        return f"{fname}.out"

    def brackets_parser(self, input_pin, output_pin):
        expression = "#"
        while expression:
            expression = ""
            for n, c in enumerate(input_pin):
                if c == ")":
                    expression = self.text_in_bracket(input_pin, n + 1)
                    inside = expression.lstrip("(").rstrip(")")

                    function = ""
                    if expression.split("(")[0]:
                        inside = expression.split("(", 1)[1].rstrip(")").split(",")[0]
                        function = expression.split("(", 1)[0]
                        if "," in expression:
                            function_params = expression.split("(", 1)[1].rstrip(")").split(",")[1:]
                        else:
                            function_params = []

                    if " " in inside:
                        new_pin = self.logic2signal(inside, output_pin)
                        input_pin = input_pin.replace(expression, new_pin)
                    else:
                        new_pin = inside
                        if expression in self.function_cache and function:
                            new_pin = self.function_cache[expression]
                        elif inside and inside[0] == "!":
                            new_pin = self.pin_not(inside[1:], output_pin)
                        elif function == "not":
                            new_pin = self.pin_not(inside, output_pin)
                        elif function == "abs":
                            new_pin = self.pin_abs(inside, output_pin)
                        elif function == "delay":
                            new_pin = self.pin_delay(inside, output_pin, function_params[0].strip(), function_params[1].strip())
                        elif function == "limit":
                            new_pin = self.pin_limit(inside, output_pin, function_params[0].strip(), function_params[1].strip())
                        elif function == "deadzone":
                            new_pin = self.pin_deadzone(inside, output_pin, function_params[0].strip(), function_params[1].strip())
                        elif function == "chargepump":
                            new_pin = self.pin_chargepump(inside)
                        elif function == "conv":
                            new_pin = self.pin_conv(inside, output_pin, function_params[0].strip(), function_params[1].strip())
                        input_pin = input_pin.replace(expression, new_pin)
                        self.function_cache[expression] = new_pin
                    break

        return input_pin

    def setp_add(self, output_pin, value):
        if output_pin not in self.setps:
            self.setps[output_pin] = value

    def fmt_add(self, line):
        if isinstance(line, list):
            self.preformated += line
        else:
            self.preformated.append(line)

    def fmt_add_top(self, line):
        if isinstance(line, list):
            self.preformated_top += line
        else:
            self.preformated_top.append(line)

    def get_type(self, parts):
        type_map = {
            "start": {
                ("analog-out-", "analog-in-", "tooloffset"): float,
            },
            "end": {
                ("counts", "increment", "number"): int,
                ("scale", "analog", "commanded", "-cmd", "feedback", "relative", "-vel", "velocity", "position"): float,
            },
        }
        for part in parts:
            for mode in ("output", "input"):
                haltype = halpins.LINUXCNC_SIGNALS[mode].get(part, {}).get("type")
                if haltype:
                    return haltype

            if part in self.halpin_info:
                pin_info = self.halpin_info.get(part, {})
                if pin_info:
                    if pin_info["boolean"]:
                        return bool
                    elif part.endswith("32"):
                        return int
                    else:
                        return float

            for mode in ("end", "start"):
                for check, htype in type_map[mode].items():
                    if mode == "end":
                        if part.endswith(check):
                            return htype
                    else:
                        if part.startswith(check):
                            return htype
        return bool

    def net_add(self, input_pin, output_pin, signal_name=None):
        if not input_pin or not output_pin:
            return
        # replace some command/operation words
        input_pin = input_pin.replace("!(", "not(")
        if output_pin[0] == "!":
            output_pin = output_pin[1:]
            input_pin = f"!{input_pin}"

        # handle multiple outputs (A,B)
        if "," in output_pin:
            for pin in output_pin.split(","):
                inpin = input_pin
                outpin = pin.strip()
                signame = signal_name
                if outpin[0] == "!":
                    outpin = outpin[1:]
                    inpin = f"!{inpin}"
                    if signame:
                        signame = f"{signame}_not"

                self.net_add(inpin, outpin, signal_name=signame)
            return

        # set default operation by type
        haltype = self.get_type([output_pin] + input_pin.split())
        if haltype is bool:
            logic = "OR"
            if input_pin[0] == "|":
                logic = "OR"
            elif input_pin[0] == "&":
                logic = "AND"
            elif output_pin[0] == "&":
                output_pin = output_pin[1:]
                logic = "AND"
            elif output_pin in self.signals_out:
                if self.signals_out[output_pin]["expression"][0] == "|":
                    logic = "OR"
                elif self.signals_out[output_pin]["expression"][0] == "&":
                    logic = "AND"
        elif haltype is int:
            logic = "S+"
        else:
            logic = "+"

        if output_pin in self.signals_out:
            # append input(s) to existing expression
            self.signals_out[output_pin]["expression"] = f"{self.signals_out[output_pin]['expression']} {logic} {input_pin}"
        else:
            self.signals_out[output_pin] = {"expression": input_pin}

        if signal_name:
            # set a predefined signal name
            if "name" not in self.signals_out[output_pin]:
                self.signals_out[output_pin]["name"] = signal_name
            elif self.signals_out[output_pin]["name"] != signal_name:
                print(f"ERROR: signalname ({signal_name}) already set for this input", output_pin)

    def get_dios(self):
        dios = 16
        for output, data in self.signals_out.items():
            if data["expression"].startswith("motion.digital-out-"):
                dios = max(dios, int(data["expression"].split("-", 2)[-1]) + 1)
            elif data["expression"].startswith("motion.digital-in-"):
                dios = max(dios, int(data["expression"].split("-", 2)[-1]) + 1)
        return dios

    def get_aios(self):
        aios = 16
        for output, data in self.signals_out.items():
            if data["expression"].startswith("motion.analog-out-"):
                aios = max(aios, int(data["expression"].split("-", 2)[-1]) + 1)
            elif data["expression"].startswith("motion.analog-in-"):
                aios = max(aios, int(data["expression"].split("-", 2)[-1]) + 1)
        return aios

    def net_write(self):
        hal_data = []
        hal_data_addf_read = []
        hal_data_addf_other = []
        hal_data_addf_write = []
        hal_data = []
        postgui_data = []

        hal_data.append("")
        for part in self.preformated_top:
            for line in part.split("\n"):
                if line.startswith("addf"):
                    function = line.split()[1]
                    if "read" in function or "send" in function or "watchdog-process" in function:
                        hal_data_addf_read.append(line)
                    elif "write" in function or "recv" in function:
                        hal_data_addf_write.append(line)
                    else:
                        hal_data_addf_other.append(line)
                else:
                    hal_data.append(line)

        hal_data.append("# read")
        hal_data += hal_data_addf_read
        hal_data.append("# process")
        hal_data += hal_data_addf_other
        hal_data.append("# write")
        hal_data += hal_data_addf_write
        hal_data.append("")

        # resolv all expressions
        for output, data in self.signals_out.items():
            cleaned_expression = data["expression"].replace("|", "").replace("&", "")
            input_pin = self.brackets_parser(f"({cleaned_expression})", output)
            input_signal = self.pin2signal(input_pin, output, data.get("name"))
            if output in self.outputs2signals:
                self.outputs2signals[output]["signals"].append(input_signal)
            else:
                self.outputs2signals[output] = {"signals": [input_signal], "target": output}

        # combine and add functions
        func_names = []
        func_personalities = []
        for func, personality in self.hal_logics.items():
            func_names.append(func)
            func_personalities.append(personality)
        if func_names:
            hal_data.append("#################################################################################")
            hal_data.append("# logic and calc components")
            hal_data.append("#################################################################################")
            hal_data.append(f"loadrt logic names={','.join(func_names)} personality={','.join(func_personalities)}")
            for fname in func_names:
                hal_data.append(f"addf {fname} servo-thread")
            hal_data.append("")
        func_names = []
        func_personalities = []
        for calc, names in self.hal_calcs.items():
            if calc in {"charge_pump"}:
                hal_data.append(f"loadrt {calc}")
            else:
                hal_data.append(f"loadrt {calc} names={','.join(names)}")
            for name in names:
                hal_data.append(f"addf {name} servo-thread")
            hal_data.append("")

        # add networks (sorting/grouping)
        postgui_data.append("#################################################################################")
        postgui_data.append("# networks")
        postgui_data.append("#################################################################################")

        sections = {}
        for target in self.signals_out:
            for pin, data in self.inputs2signals.items():
                if data["signal"].startswith("j"):
                    continue
                if data["target"] == target:
                    component = pin.split(".", 1)[0]
                    if component in self.POSTGUI_COMPONENTS:
                        postgui_data.append(f"net {data['signal']:36s} <= {pin}")
                    elif component not in self.VIRTUAL_COMPONENTS:
                        prefix = pin.split(".")[0]
                        if prefix not in sections:
                            sections[prefix] = {}
                        sections[prefix][pin] = ("<=", data["signal"])

        for target in self.signals_out:
            for pin, data in self.outputs2signals.items():
                component = pin.split(".", 1)[0]
                if data["target"] == target:
                    for signal in data["signals"]:
                        if signal.startswith("j"):
                            continue
                        if component in self.POSTGUI_COMPONENTS:
                            postgui_data.append(f"net {signal:36s} => {pin}")
                        elif component not in self.VIRTUAL_COMPONENTS:
                            prefix = pin.split(".")[0]
                            if prefix not in sections:
                                sections[prefix] = {}
                            sections[prefix][pin] = ("=>", signal)

        for section, data in sections.items():
            hal_data.append("#################################################################################")
            hal_data.append(f"# {section}")
            hal_data.append("#################################################################################")
            prefix_last = ""
            for pin in sorted(data):
                # little bit more grouping
                prefix = ".".join(pin.split(".")[:-1])[:-2]
                if prefix != prefix_last and prefix_last != "":
                    hal_data.append("")
                prefix_last = prefix

                arrow, signal = data[pin]
                hal_data.append(f"net {signal:36s} {arrow} {pin}")
            hal_data.append("")
        postgui_data.append("")

        # joints only
        for joint in range(0, 12):
            found = False
            for pin, value in self.setps.items():
                if f"[JOINT_{joint}]" in str(value):
                    found = True

            for pin, data in self.inputs2signals.items():
                if data["signal"].startswith(f"j{joint}"):
                    found = True

            for pin, data in self.outputs2signals.items():
                for signal in data["signals"]:
                    if signal.startswith(f"j{joint}"):
                        found = True

            if not found:
                continue

            hal_data.append("#################################################################################")
            hal_data.append(f"# joint-{joint}")
            hal_data.append("#################################################################################")

            for pin, value in self.setps.items():
                if f"[JOINT_{joint}]" in str(value):
                    signal = self.outputs2signals.get(pin) or self.inputs2signals.get(pin)
                    if not signal:
                        component = pin.split(".", 1)[0]
                        if component in self.POSTGUI_COMPONENTS:
                            hal_data.append(f"# setp {pin:35s} {value:6} (in postgui)")
                            postgui_data.append(f"setp {pin:35s} {value}")
                        else:
                            hal_data.append(f"setp {pin:35s} {value}")
                    else:
                        hal_data.append(f"# setp {pin:35s} {value:6} (already linked to {', '.join(signal.get('signals', [signal.get('signal', '?')]))})")

            for pin, data in self.inputs2signals.items():
                component = pin.split(".", 1)[0]
                if data["signal"].startswith(f"j{joint}"):
                    component = pin.split(".", 1)[0]
                    if component in self.POSTGUI_COMPONENTS:
                        hal_data.append(f"# net {data['signal']:36s} <= {pin} (in postgui)")
                        postgui_data.append(f"net {data['signal']:36s} <= {pin}")
                    elif component in self.VIRTUAL_COMPONENTS:
                        hal_data.append(f"# net {data['signal']:36s} <= {pin} (virtual pin)")
                    else:
                        hal_data.append(f"net {data['signal']:36s} <= {pin}")

            for pin, data in self.outputs2signals.items():
                component = pin.split(".", 1)[0]
                for signal in data["signals"]:
                    if signal.startswith(f"j{joint}"):
                        if component in self.POSTGUI_COMPONENTS:
                            hal_data.append(f"# net {signal:36s} => {pin} (in postgui)")
                            postgui_data.append(f"net {signal:36s} => {pin}")
                        elif component in self.VIRTUAL_COMPONENTS:
                            hal_data.append(f"# net {signal:36s} => {pin} (virtual pin)")
                        else:
                            hal_data.append(f"net {signal:36s} => {pin}")

            hal_data.append("")

        if self.setps:
            hal_data.append("#################################################################################")
            hal_data.append("# setp")
            hal_data.append("#################################################################################")

            postgui_data.append("#################################################################################")
            postgui_data.append("# setp")
            postgui_data.append("#################################################################################")

            for pin in sorted(list(self.setps)):
                value = self.setps[pin]
                if "[JOINT_" in str(value):
                    continue

                signal = self.outputs2signals.get(pin) or self.inputs2signals.get(pin)
                if not signal:
                    component = pin.split(".", 1)[0]
                    if component in self.POSTGUI_COMPONENTS:
                        hal_data.append(f"# setp {pin:36s}   {value:6} (in postgui)")
                        postgui_data.append(f"setp {pin:36s}   {value}")
                    else:
                        hal_data.append(f"setp {pin:36s}   {value}")
                else:
                    hal_data.append(f"# setp {pin:36s}   {value:6} (already linked to {', '.join(signal.get('signals', [signal.get('signal', '?')]))})")

            hal_data.append("")
            postgui_data.append("")

        hal_data.append("#################################################################################")
        hal_data.append("# preformated")
        hal_data.append("#################################################################################")
        for line in self.preformated:
            hal_data.append(line)

        return (hal_data, postgui_data)

    def joint_add(self, parent, axis_name, joint, mode, cmd_halname, feedback_halname=None, scale_halname=None, feedback_scale_halname=None, enable_halname=None, fault_halname=None, pid_num=None):
        linuxcnc_config = parent.project.config["jdata"].get("linuxcnc", {})
        machinetype = linuxcnc_config.get("machinetype")
        self.setp_add(f"{scale_halname}", f"[JOINT_{joint}]SCALE_OUT")
        if feedback_scale_halname:
            self.setp_add(f"{feedback_scale_halname}", f"[JOINT_{joint}]SCALE_IN")

        if mode == "position":
            if machinetype == "corexy" and axis_name in {"X", "Y"}:
                corexy_axis = "beta"
                if axis_name == "X":
                    corexy_axis = "alpha"
                self.net_add(f"joint.{joint}.motor-pos-cmd", f"corexy.j{joint}-motor-pos-cmd", f"j{joint}pos-cmd")
                self.net_add(f"corexy.{corexy_axis}-cmd", f"{cmd_halname}", f"j{joint}pos-cmd-{corexy_axis}")
                self.net_add(f"corexy.{corexy_axis}-cmd", f"corexy.{corexy_axis}-fb", f"j{joint}pos-cmd-{corexy_axis}")
                self.net_add(f"corexy.j{joint}-motor-pos-fb", f"joint.{joint}.motor-pos-fb", f"j{joint}pos-fb-{corexy_axis}")
            else:
                self.net_add(f"joint.{joint}.motor-pos-cmd", f"{cmd_halname}", f"j{joint}pos-cmd")
                self.net_add(f"{feedback_halname}", f"joint.{joint}.motor-pos-fb", f"j{joint}pos-fb")
                # self.net_add(f"joint.{joint}.motor-pos-cmd", f"joint.{joint}.motor-pos-fb", f"j{joint}pos-cmd")
        else:
            for key in ("Pgain", "Igain", "Dgain", "bias", "FF0", "FF1", "FF2", "deadband", "maxoutput"):
                parent.halg.setp_add(f"pid.{joint}.{key}", f"[JOINT_{joint}]{key.replace('gain', '').upper()}")

            if machinetype == "corexy" and axis_name in {"X", "Y"}:
                corexy_axis = "beta"
                if axis_name == "X":
                    corexy_axis = "alpha"
                self.net_add(f"pid.{pid_num}.output", f"{cmd_halname}", f"j{joint}vel-cmd")
                self.net_add(f"joint.{joint}.motor-pos-cmd", f"corexy.j{joint}-motor-pos-cmd", f"j{joint}pos-cmd")
                self.net_add(f"corexy.{corexy_axis}-cmd", f"pid.{pid_num}.command", f"j{joint}pos-cmd-{corexy_axis}")
                self.net_add(f"{feedback_halname}", f"corexy.{corexy_axis}-fb", f"j{joint}pos-fb-{corexy_axis}")
                self.net_add(f"{feedback_halname}", f"pid.{joint}.feedback", f"j{joint}pos-fb-{corexy_axis}")
                self.net_add(f"corexy.j{joint}-motor-pos-fb", f"joint.{joint}.motor-pos-fb", f"j{joint}pos-fb")
            else:
                self.net_add(f"pid.{pid_num}.output", f"{cmd_halname}", f"j{joint}vel-cmd")
                self.net_add(f"joint.{joint}.motor-pos-cmd", f"pid.{pid_num}.command", f"j{joint}pos-cmd")
                self.net_add(f"{feedback_halname}", f"joint.{joint}.motor-pos-fb", f"j{joint}motor-pos-fb")
                self.net_add(f"{feedback_halname}", f"pid.{joint}.feedback", f"j{joint}motor-pos-fb")
            if machinetype in {"ldelta", "rdelta"} and axis_name in {"X", "Y", "Z", "XYZ"}:
                self.net_add(f"{feedback_halname}", f"lineardelta.joint{joint}", f"j{joint}motor-pos-fb")

            self.net_add(f"joint.{joint}.amp-enable-out", f"pid.{pid_num}.enable", f"j{joint}enable")

        if enable_halname:
            self.net_add(f"joint.{joint}.amp-enable-out", f"{enable_halname}", f"j{joint}enable")
        if fault_halname:
            self.net_add(f"{fault_halname}", f"joint.{joint}.amp-fault-in", f"j{joint}fault")


if __name__ == "__main__":
    halg = hal_generator()

    halg.net_add("!rio.input1", "hal.output2")
    halg.net_add("rio.input1", "hal.output1")
    halg.net_add("rio.input1 and !rio.input2", "hal.output3")

    halg.net_add("!pio.input1", "hal.pio_output2")
    halg.net_add("pio.input1", "hal.pio_output1")
    halg.net_add("pio.input1 and !pio.input2", "hal.pio_output3")

    halg.net_add("rio.input2 or pyvcp.input3", "hal.or_out")
    halg.net_add("rio.s32_1 + rio.s32_2 + rio.s32_3", "hal.out-sint")
    halg.net_add("(rio.float_1 * rio.float_2) / (rio.float_3 * rio.float_4)", "hal.out-float")
    halg.net_add("rio.s32_1 - rio.s32_2", "hal.out-sint")

    halg.net_add("|rio.input2", "hal.or_out")
    halg.net_add("rio.input3", "hal.or_out")

    halg.net_add("&rio.input4", "pyvcp.and_out")
    halg.net_add("rio.input5", "pyvcp.and_out")

    halg.net_add("&rio.input8", "pyvcp.complex_out")
    halg.net_add("(sig:existing or rio.input5 or rio.input6) and rio.input7", "pyvcp.complex_out", "my_complex_out")

    halg.net_add("(rio.input5 or rio.input6)", "rio.orout1")
    halg.net_add("(rio.input5 or rio.input6)", "rio.orout2")

    halg.setp_add("pyvcp.outval", "123")
    halg.setp_add("rio.outval", "123")
    halg.setp_add("rio.orout1", "0")
    halg.setp_add("rio.s32_1", "100")

    halg.net_add("pio.input4", "cp.and_out, !cp.and_out2, !cp.and_out3", "multiout")

    (hal_data, postgui_data) = halg.net_write()
    print("\n".join(hal_data))
    print("---------------------------------")
    print("\n".join(postgui_data))
