import copy
import glob
import importlib
import json
import os
import re
import shutil
from struct import pack, unpack
import sys
import traceback

from .generator.Gateware import Gateware
from .generator.LinuxCNC import LinuxCNC
from .generator.Firmware import Firmware

riocore_path = os.path.dirname(__file__)


class Plugins:
    def __init__(self):
        self.plugin_modules = {}
        self.plugin_instances = []

    def list(self):
        plugins = []
        for plugin_path in sorted(glob.glob(f"{riocore_path}/plugins/*/plugin.py")):
            plugin_name = os.path.basename(os.path.dirname(plugin_path))
            plugins.append({"name": plugin_name, "path": plugin_path})
        return plugins

    def info(self, plugin_name):
        output = []
        self.load_plugins({"plugins": [{"type": plugin_name}]})
        plugin = self.plugin_instances[-1]

        output.append(f"# {plugin.NAME}")

        if plugin.INFO:
            output.append(f"**{plugin.INFO}**")
            output.append("")
        if plugin.DESCRIPTION:
            output.append(plugin.DESCRIPTION)
            output.append("")
        if plugin.KEYWORDS:
            output.append(f"Keywords: {plugin.KEYWORDS}")
            output.append("")

        plugin_path = f"{riocore_path}/plugins/{plugin_name}"
        image_path = f"{plugin_path}/image.png"
        if os.path.isfile(image_path):
            output.append("")
            output.append("![image.png](image.png)")
            output.append("")

        if plugin.LIMITATIONS:
            output.append("## Limitations")
            for key, values in plugin.LIMITATIONS.items():
                output.append(f"* {key}: {', '.join(values)}")
            output.append("")

        output.append("## Basic-Example:")
        output.append("```")
        output.append(json.dumps(plugin.basic_config(), indent=4))
        output.append("```")
        output.append("")
        output.append("## Pins:")
        output.append("*FPGA-pins*")
        output.append(plugin.show_pins())
        output.append("")
        output.append("## Options:")
        output.append("*user-options*")
        output.append(plugin.show_options())
        output.append("")
        output.append("## Signals:")
        output.append("*signals/pins in LinuxCNC*")
        output.append(plugin.show_signals())
        output.append("")
        output.append("## Interfaces:")
        output.append("*transport layer*")
        output.append(plugin.show_interfaces())
        output.append("")
        output.append("## Full-Example:")
        output.append("```")
        output.append(json.dumps(plugin.full_config(), indent=4))
        output.append("```")
        output.append("")
        if plugin.VERILOGS:
            output.append("## Verilogs:")
            for vfile in plugin.VERILOGS:
                output.append(f" * [{vfile}]({vfile})")
            output.append("")
        return "\n".join(output)

    def load_plugin(self, plugin_id, plugin_config, system_setup=None):
        try:
            plugin_type = plugin_config["type"]
            if plugin_type not in self.plugin_modules:
                if os.path.isfile(f"{riocore_path}/plugins/{plugin_type}/plugin.py"):
                    # print(f"loading plugin {plugin_type}")
                    self.plugin_modules[plugin_type] = importlib.import_module(".plugin", f"riocore.plugins.{plugin_type}")
                elif os.path.isfile(f"{riocore_path}/plugins/{plugin_type}/{plugin_type}.v"):
                    if self.plugin_builder(plugin_type, f"{riocore_path}/plugins/{plugin_type}/{plugin_type}.v", plugin_config):
                        self.plugin_modules[plugin_type] = importlib.import_module(".plugin", f"riocore.plugins.{plugin_type}")
                elif not plugin_type or plugin_type[0] != "_":
                    print(f"WARNING: plugin not found: {plugin_type}")

            if plugin_type in self.plugin_modules:
                plugin_instance = self.plugin_modules[plugin_type].Plugin(plugin_id, plugin_config, system_setup=system_setup)
                for pin_name, pin_config in plugin_instance.pins().items():
                    if "pin" in pin_config and pin_config["pin"] and not pin_config["pin"].startswith("EXPANSION"):
                        if pin_config["pin"] == "" or pin_config["pin"] is None:
                            print(f"WARNING: pin '{pin_name}' of '{plugin_instance.instances_name}' is not set / removed")
                            del pin_config["pin"]
                self.plugin_instances.append(plugin_instance)

                # if not os.path.isfile(f"{riocore_path}/plugins/{plugin_type}/testb.v") and os.path.isfile(f"{riocore_path}/plugins/{plugin_type}/{plugin_type}.v"):
                #    self.testbench_builder(plugin_type, plugin_instance)

                return plugin_instance
        except Exception:
            print(f"ERROR: loading plugin: {plugin_id} / {plugin_config}")
            print("##################################")
            traceback.print_exc(file=sys.stdout)
            print("##################################")

    def load_plugins(self, config, system_setup=None):
        if config["plugins"]:
            for plugin_id, plugin_config in enumerate(config["plugins"]):
                self.load_plugin(plugin_id, plugin_config, system_setup=system_setup)
            return self.plugin_instances
        return None

    def testbench_builder(self, plugin_type, plugin_instance):
        print(f"try to build testbench for {plugin_type}")

        speed = int(plugin_instance.system_setup["jdata"]["clock"]["speed"])
        time_steps = 50
        max_time = 3000000
        diff_time = max_time // time_steps

        if plugin_instance.gateware_instances():
            tbfile = []
            tbfile.append("")
            tbfile.append("`timescale 1ns/100ps")
            tbfile.append("")
            tbfile.append("module testb;")
            tbfile.append("    reg clk = 0;")
            tbfile.append("    always #1 clk = !clk;")
            tbfile.append("")

            tbfile.append("    // pins")
            if plugin_instance.pins():
                pins = plugin_instance.pins()
            else:
                pins = plugin_instance.PINDEFAULTS
                for pin_name, pin_config in pins.items():
                    pins[pin_name]["pin"] = "11"

            for pin_name, pin_config in pins.items():
                if pin_config["direction"] == "output":
                    tbfile.append(f"    wire {pin_name};")
                else:
                    tbfile.append(f"    reg {pin_name} = 0;")
            tbfile.append("    // interface")
            for data_name, data_config in plugin_instance.interface_data().items():
                size = data_config["size"]
                if data_config["direction"] == "output":
                    if size > 1:
                        tbfile.append(f"    reg signed [{size-1}:0] {data_name} = {size}'d0;")
                    else:
                        if data_name == "enable":
                            tbfile.append(f"    reg {data_name} = 1;")
                        else:
                            tbfile.append(f"    reg {data_name} = 0;")
                else:
                    if size > 1:
                        tbfile.append(f"    wire signed [{size-1}:0] {data_name};")
                    else:
                        tbfile.append(f"    wire {data_name};")

            tbfile.append("")
            tbfile.append("    initial begin")
            tbfile.append('        $dumpfile("testb.vcd");')
            tbfile.append("        $dumpvars(0, clk);")
            pn = 1
            tbfile.append("        // pins")
            for pin_name, pin_config in pins.items():
                tbfile.append(f"        $dumpvars({pn}, {pin_name});")
                pn += 1
            tbfile.append("        // interface")
            for data_name, data_config in plugin_instance.interface_data().items():
                tbfile.append(f"        $dumpvars({pn}, {data_name});")
                pn += 1

            time_pos = 0
            tbfile.append("")
            for nn in range(time_steps):
                tbfile.append(f"        #{diff_time}")
                for data_name, data_config in plugin_instance.interface_data().items():
                    if data_config["direction"] == "output":
                        if data_config["size"] > 1:
                            if data_name in {"dty", "velocity", "position", "frequency"}:
                                tbfile.append(f"        {data_name} = {speed // (255 * (nn + 1))};")
                                time_pos += diff_time

            tbfile.append("")
            tbfile.append(f"        # {diff_time} $finish;")
            tbfile.append("    end")
            tbfile.append("")

            for instance_name, instance_config in plugin_instance.gateware_instances().items():
                instance_module = instance_config.get("module")
                instance_parameter = instance_config.get("parameter")
                instance_arguments = instance_config.get("arguments")
                instance_direct = instance_config.get("direct")
                if not instance_direct:
                    if instance_arguments:
                        if instance_parameter:
                            tbfile.append(f"    {instance_module} #(")
                            parameters_list = []
                            for parameter_name, parameter_value in instance_parameter.items():
                                parameters_list.append(f".{parameter_name}({parameter_value})")
                            parameters_string = ",\n        ".join(parameters_list)
                            tbfile.append(f"        {parameters_string}")
                            tbfile.append(f"    ) {instance_name} (")
                        else:
                            tbfile.append(f"    {instance_module} {instance_name} (")
                        arguments_list = []
                        for argument_name, argument_value in instance_arguments.items():
                            arguments_list.append(f".{argument_name}({argument_name})")
                        for pin_name, pin_config in pins.items():
                            if f"({pin_name})" not in arguments_list:
                                arguments_list.append(f".{pin_name}({pin_name})")

                        arguments_string = ",\n        ".join(arguments_list)
                        tbfile.append(f"        {arguments_string}")
                        tbfile.append("    );")

            tbfile.append("")
            tbfile.append("endmodule")
            tbfile.append("")
            open(f"{riocore_path}/plugins/{plugin_type}/testb.v", "w").write("\n".join(tbfile))

            gtkwfile = []
            gtkwfile.append("[*]")
            gtkwfile.append("[*] GTKWave Analyzer v3.4.0 (w)1999-2022 BSI")
            gtkwfile.append("[*] Thu Apr 25 12:05:02 2024")
            gtkwfile.append("[*]")
            gtkwfile.append('[dumpfile] "testb.vcd"')
            gtkwfile.append('[dumpfile] "testb.vcd"')
            gtkwfile.append("[timestart] 0")
            gtkwfile.append("@30")
            gtkwfile.append("testb.clk")

            pn = 31
            for pin_name, pin_config in pins.items():
                gtkwfile.append(f"@{pn}")
                gtkwfile.append(f"testb.{pin_name}")
                pn += 1
            for data_name, data_config in plugin_instance.interface_data().items():
                size = data_config["size"]
                gtkwfile.append(f"@{pn}")
                if size > 1:
                    gtkwfile.append(f"testb.{data_name}[{size-1}:0]")
                else:
                    gtkwfile.append(f"testb.{data_name}")
                pn += 1

            gtkwfile.append("")
            open(f"{riocore_path}/plugins/{plugin_type}/testb.gtkw", "w").write("\n".join(gtkwfile))

            makefile = []
            makefile.append("")
            makefile.append("all: testb")
            makefile.append("")
            makefile.append("testb:")
            makefile.append(f"	iverilog -Wall -o testb.out testb.v {plugin_type}.v")
            makefile.append("	vvp testb.out")
            makefile.append("	#gtkwave testb.vcd")
            makefile.append("	gtkwave testb.gtkw")
            makefile.append("")
            makefile.append("clean:")
            makefile.append("	rm -rf testb.out testb.vcd")
            makefile.append("")
            open(f"{riocore_path}/plugins/{plugin_type}/Makefile", "w").write("\n".join(makefile))

            print(f"(cd {riocore_path}/plugins/{plugin_type} ; make)")

            return True

        return False

    def plugin_builder(self, plugin_name, verilog_file, plugin_config):
        print(f"try to autoload plugin from {plugin_name}.v")
        verilog_data = open(verilog_file, "r").read()
        x = re.search(r"(module\s+)(?P<name>[a-z0-9_]+)\s+(?P<parameters>#\([^\).]*\))?\s*(?P<arguments>\([^\).]*\));", verilog_data)
        if x is not None:
            if plugin_name != x.group("name"):
                print(f"ERROR: wrong toplevel name: {x.group('name')}, needs: {plugin_name}")
                return False

            arguments = x.group("arguments")
            parameters = x.group("parameters")
            pindefaults = {}
            interface = {}
            signals = {}
            parameter = {}
            has_clock = False
            parameter_dict = {}
            if parameters:
                for parameter in parameters.strip("#()").split(","):
                    parameter_name = ""
                    parameter_default = ""
                    for part in re.split(r"[\s=]", parameter):
                        part = part.strip()
                        if not part:
                            pass
                        elif not parameter_name and part.startswith("["):
                            pass
                        elif not parameter_name and part != "parameter" and "'" not in part:
                            parameter_name = part
                        elif parameter_name and part != "=":
                            parameter_default = part
                    if parameter_name:
                        parameter_dict[parameter_name] = {"default": parameter_default}
            is_interface = False
            if "tx_data" in arguments and "rx_data" in arguments and "pkg_timeout" in arguments:
                is_interface = True
            for argument in arguments.strip("()").split(","):
                argument_size = 1
                argument_direction = ""
                argument_name = ""
                for part in argument.split():
                    if part.startswith("["):
                        argument_size_end, argument_size_start = part.strip("[]").split(":")
                        if argument_size_end.isnumeric() and argument_size_start.isnumeric():
                            argument_size = int(argument_size_end) - int(argument_size_start) + 1
                        else:
                            print(f"WARNING: can not parse size: {part}, using 32")
                            argument_size = 32
                    elif part in {"reg", "wire", "=", "signed", "unsigned"}:
                        pass
                    elif part in {"input", "output", "inout"}:
                        argument_direction = part
                    elif not argument_name:
                        argument_name = part

                print(argument_name, argument_size, argument_name in plugin_config.get("pins", {}))

                if argument_name in {"clk"}:
                    has_clock = True
                elif is_interface and argument_name in {"pkg_timeout"}:
                    pass
                elif argument_size == 1 and plugin_config.get("init") is True:
                    pindefaults[argument_name] = {
                        "direction": argument_direction,
                    }
                elif argument_size == 1 and argument_name in plugin_config.get("pins", {}):
                    pindefaults[argument_name] = {
                        "direction": argument_direction,
                    }
                elif is_interface:
                    pass
                else:
                    interface[argument_name] = {
                        "size": argument_size,
                        "direction": {"input": "output", "output": "input"}.get(argument_direction),
                    }
                    signals[argument_name] = {
                        "size": argument_size,
                        "direction": {"input": "output", "output": "input"}.get(argument_direction),
                    }
            if not has_clock:
                print("FAILED: can not find clock pin")
            elif not pindefaults:
                print("FAILED: can not find io pin's")
            elif not interface and not signals and not is_interface:
                print("FAILED: can not find interface/signals")
            else:
                initfile = []
                initfile.append("")
                initfile.append("from riocore.plugins import PluginBase")
                initfile.append("")
                initfile.append("class Plugin(PluginBase):")
                initfile.append("")
                initfile.append("    def setup(self):")
                initfile.append(f'        self.NAME = "{plugin_name}"')
                initfile.append(f'        self.VERILOGS = ["{plugin_name}.v"]')
                initfile.append("        self.PINDEFAULTS = {")
                for pin_name, pin_setup in pindefaults.items():
                    initfile.append(f'            "{pin_name}": {{')
                    initfile.append(f"                \"direction\": \"{pin_setup['direction']}\",")
                    initfile.append('                "invert": False,')
                    initfile.append('                "pull": None,')
                    initfile.append("            },")
                initfile.append("        }")
                if interface:
                    initfile.append("        self.INTERFACE = {")
                    for interface_name, interface_setup in interface.items():
                        initfile.append(f'            "{interface_name}": {{')
                        initfile.append(f"                \"size\": {interface_setup['size']},")
                        initfile.append(f"                \"direction\": \"{interface_setup['direction']}\",")
                        initfile.append("            },")
                    initfile.append("        }")
                if signals:
                    initfile.append("        self.SIGNALS = {")
                    for signal_name, signal_setup in signals.items():
                        initfile.append(f'            "{signal_name}": {{')
                        initfile.append(f"                \"direction\": \"{signal_setup['direction']}\",")
                        if signal_setup["size"] == 1:
                            initfile.append('                "bool": True,')
                        initfile.append("            },")
                    initfile.append("        }")
                if is_interface:
                    initfile.append('        self.TYPE = "interface"')
                initfile.append("")
                if parameter_dict:
                    initfile.append("    def gateware_instances(self):")
                    initfile.append("        instances = self.gateware_instances_base()")
                    initfile.append("        instance = instances[self.instances_name]")
                    initfile.append('        instance_predefines = instance["predefines"]')
                    initfile.append('        instance_parameter = instance["parameter"]')
                    initfile.append('        instance_arguments = instance["arguments"]')
                    for parameter_name, parameter_setup in parameter_dict.items():
                        if parameter_name in {"DIVIDER"}:
                            initfile.append("        # example")
                            initfile.append('        # frequency = int(self.plugin_setup.get("frequency", 100))')
                            initfile.append(f'        # {parameter_name.lower()} = self.system_setup["speed"] // frequency')
                            initfile.append(f'        # instance_parameter["{parameter_name}"] = {parameter_name.lower()}')
                        initfile.append(f"        # instance_parameter[\"{parameter_name}\"] = self.plugin_setup.get(\"{parameter_name.lower()}\", \"{parameter_setup['default']}\")")
                    initfile.append("        return instances")
                    initfile.append("")
                if os.path.isfile(f"{riocore_path}/plugins/{plugin_name}/plugin.py"):
                    print(f"WARNING: file allready exsits: {riocore_path}/plugins/{plugin_name}/plugin.py")
                    print("\n".join(initfile))
                    print("")
                else:
                    print(f"INFO: writing plugin setup to {riocore_path}/plugins/{plugin_name}/plugin.py (please edit)")
                    open(f"{riocore_path}/plugins/{plugin_name}/plugin.py", "w").write("\n".join(initfile))
                    print("")

                if plugin_config.get("init") is True:
                    print("# config example:")
                    print("    {")
                    print(f'        "type": "{plugin_name}",')
                    print('        "pins": {')
                    pn = 0
                    for pin_name, pin_setup in pindefaults.items():
                        print(f'            "{pin_name}": {{')
                        print(f'                "pin": "{pn}",')
                        print("            },")
                        pn += 1
                    print("        }")
                    print("    },")
                    print("")
                    print(".... OK")
                return True
        print(".... Failed")
        return False


class Project:
    def __init__(self, configuration, output_path=None):
        plugins = Plugins()
        self.load_config(configuration, output_path)
        self.plugin_instances = plugins.load_plugins(self.config, system_setup=self.config)
        self.calc_buffersize()
        self.generator_linuxcnc = LinuxCNC(self)
        if self.config["toolchain"] == "platformio":
            self.generator_firmware = Firmware(self)
        else:
            self.generator_gateware = Gateware(self)

        # check names
        varnames = {}
        for plugin_instance in self.plugin_instances:
            for signal_name, signal_config in plugin_instance.signals().items():
                varname = signal_config["varname"]
                if varname not in varnames:
                    varnames[varname] = plugin_instance.instances_name
                else:
                    print(f"ERROR: varname allready exist: {varname} ({plugin_instance.instances_name} / {varnames[varname]})")

    def get_path(self, path):
        if os.path.exists(path):
            return path
        elif os.path.exists(f"{riocore_path}/{path}"):
            return f"{riocore_path}/{path}"
        print(f"path not found: {path} or {riocore_path}/{path}")
        exit(1)

    def get_boardpath(self, board):
        pathes = [
            f"{board}.json",
            f"{riocore_path}/boards/{board}.json",
            f"{riocore_path}/boards/{board}/board.json",
        ]
        for path in pathes:
            if os.path.exists(path):
                return path
        print(f"can not find board: {board}")
        exit(1)

    def load_config(self, configuration, output_path=None):
        project = {}

        if output_path is None:
            output_path = "Output"

        # project["config"] = configuration
        if isinstance(configuration, str) and configuration[0] == "{":
            project = {"jdata": json.loads(configuration)}
            project["json_file"] = None
        else:
            if not os.path.isfile(configuration):
                print("")
                print(f"this is not a file: {configuration}")
                print("")
                exit(1)
            try:
                with open(configuration, "r") as f:
                    data = f.read()
            except IOError as err:
                print("")
                print(err)
                print("")
                exit(1)

            try:
                project["jdata"] = json.loads(data)
            except ValueError as err:
                print("")
                print(f"JSON error: {err}")
                print("please check your json syntax")
                print("")
                exit(1)
            project["json_file"] = configuration
            project["json_path"] = os.path.dirname(configuration)

        project["plugins"] = copy.deepcopy(project["jdata"].get("plugins"))
        project["board_data"] = {}

        # loading board data
        board = project["jdata"].get("boardcfg")
        if board:
            print(f"loading board setup: {board}")
            board_file = self.get_boardpath(board)
            bdata = open(board_file, "r").read()
            project["board_data"] = json.loads(bdata)
            if "name" in project["board_data"]:
                project["board"] = project["board_data"]["name"]
            for key, value in project["board_data"].items():
                if key not in project["jdata"]:
                    project["jdata"][key] = value

        if "flashcmd" in project["jdata"]:
            project["flashcmd"] = project["jdata"]["flashcmd"]

        # loading modules
        project["modules"] = {}
        modules_path = self.get_path("modules")
        for path in sorted(glob.glob(f"{modules_path}/*/module.json")):
            module = path.split("/")[-2]
            mdata = open(path, "r").read()
            project["modules"][module] = json.loads(mdata)

        # import module data
        for slot_n, slot in enumerate(project["jdata"].get("slots", [])):
            spins = slot["pins"]
            slotname = slot.get("name", f"slot{slot_n}")
            modules = []
            # check old config style
            if "module" in slot:
                module = slot.get("module")
                ssetup = slot.get("setup")
                print(f"WARNING: found old config style for slot modules, please update: {module}")
                modules.append(
                    {
                        "slot": slotname,
                        "module": module,
                        "setup": ssetup,
                    }
                )

            # check new config style
            modules += project["jdata"].get("modules", {})

            # merge modules
            for modulesetup in modules:
                if modulesetup.get("slot") != slotname:
                    continue
                module = modulesetup.get("module", [])
                ssetup = modulesetup.get("setup", {})
                if module in project["modules"]:
                    module_data = copy.deepcopy(project["modules"][module])
                    if "enable" in module_data:
                        project["enable"] = module_data["enable"]
                        project["enable"]["pin"] = slot["pins"][module_data["enable"]["pin"]]
                    if "plugins" in module_data:
                        for jn, msetup in enumerate(module_data.get("plugins", [])):
                            msetup_name = msetup.get("name")
                            if msetup_name and msetup_name in ssetup:
                                self.setup_merge(ssetup[msetup_name], msetup)
                            else:
                                ssetup[msetup_name] = copy.deepcopy(msetup)
                            # rewrite pins
                            for pname, pin in ssetup.get(msetup_name, {}).get("pins", {}).items():
                                if "pin" in pin:
                                    if "[" in pin["pin"]:
                                        realpin = pin["pin"]
                                        if isinstance(realpin, dict):
                                            realpin = realpin["pin"]
                                    else:
                                        realpin = spins[pin["pin"]]
                                        if isinstance(realpin, dict):
                                            realpin = realpin["pin"]
                                ssetup[msetup_name]["pins"][pname]["pin"] = realpin
                            module_data["plugins"][jn] = ssetup[msetup_name]
                        # merge into jdata
                        project["plugins"] += module_data["plugins"]
                else:
                    print(f"ERROR: module {module} not found")
                    exit(1)

        self.config = project
        self.config["speed"] = int(project["jdata"]["clock"]["speed"])
        self.config["osc_clock"] = int(project["jdata"]["clock"].get("osc", 0))
        self.config["sysclk_pin"] = project["jdata"]["clock"]["pin"]
        self.config["error_pin"] = project["jdata"].get("error", {}).get("pin")
        self.config["output_path"] = f"{output_path}/{project['jdata']['name']}"
        self.config["name"] = project["jdata"]["name"]
        self.config["toolchain"] = project["jdata"]["toolchain"]
        self.config["family"] = project["jdata"].get("family", "UNKNOWN")
        self.config["type"] = project["jdata"].get("type", "UNKNOWN")
        self.config["package"] = project["jdata"].get("package", "UNKNOWN")

    def setup_merge(self, setup, defaults):
        for key, value in defaults.items():
            if key not in setup:
                setup[key] = copy.deepcopy(value)
            elif isinstance(value, dict):
                self.setup_merge(setup[key], value)

    def calc_buffersize(self):
        self.header_size = 32
        self.input_size = 0
        self.output_size = 0
        self.interface_sizes = set()
        self.multiplexed_input = 0
        self.multiplexed_input_size = 0
        self.multiplexed_output = 0
        self.multiplexed_output_size = 0
        self.multiplexed_output_id = 0
        for plugin_instance in self.plugin_instances:
            for data_name, data_config in plugin_instance.interface_data().items():
                self.interface_sizes.add(data_config["size"])
                variable_size = data_config["size"]
                multiplexed = data_config.get("multiplexed", False)
                if data_config["direction"] == "input":
                    if multiplexed:
                        self.multiplexed_input += 1
                        self.multiplexed_input_size = (max(self.multiplexed_input_size, variable_size) + 7) // 8 * 8
                        if self.multiplexed_input_size < 8:
                            self.multiplexed_input_size = 8
                    else:
                        self.input_size += variable_size
                elif data_config["direction"] == "output":
                    if multiplexed:
                        self.multiplexed_output += 1
                        self.multiplexed_output_size = (max(self.multiplexed_output_size, variable_size) + 7) // 8 * 8
                        if self.multiplexed_output_size < 8:
                            self.multiplexed_output_size = 8
                    else:
                        self.output_size += variable_size

        if self.multiplexed_input:
            self.input_size += self.multiplexed_input_size + 8
        if self.multiplexed_output:
            self.output_size += self.multiplexed_output_size + 8

        self.input_size = self.input_size + self.header_size
        self.output_size = self.output_size + self.header_size
        self.buffer_size = (max(self.input_size, self.output_size) + 7) // 8 * 8
        self.buffer_bytes = self.buffer_size // 8
        self.config["buffer_size"] = self.buffer_size

    def get_bype_pos(self, bitpos, variable_size):
        byte_pos = (bitpos + 7) // 8
        byte_size = (variable_size + 7) // 8
        byte_start = byte_pos - byte_size
        bit_offset = (bitpos - variable_size) % 8
        return (byte_start, byte_size, bit_offset)

    def get_interface_data(self):
        interface_data = []
        for size in sorted(self.interface_sizes, reverse=True):
            for plugin_instance in self.plugin_instances:
                for data_name, data_config in plugin_instance.interface_data().items():
                    if data_config["size"] == size:
                        interface_data.append([size, plugin_instance, data_name, data_config])
        return interface_data

    def connect(self, cstr):
        connection = None
        for ppath in sorted(glob.glob(f"{os.path.dirname(__file__)}/interfaces/*/*.py")):
            plugin = os.path.basename(os.path.dirname(ppath))
            interface = importlib.import_module(".interface", f"riocore.interfaces.{plugin}")
            if interface.Interface.check(cstr):
                print(f"connection via: {plugin}")
                connection = interface.Interface(cstr)
                break

        if connection is None:
            print(f"ERROR: no interface found for connection-string: {cstr}")
            exit(1)
        self.connection = connection
        return connection

    def transfare(self, data):
        return self.connection.transfare(data)

    def signal_value_set(self, name, value):
        for plugin_instance in self.plugin_instances:
            for signal_name, signal_config in plugin_instance.signals().items():
                direction = signal_config["direction"]
                virtual = signal_config.get("virtual", False)
                if virtual:
                    # swap direction vor virt signals
                    if direction == "input":
                        direction = "output"
                    else:
                        direction = "input"
                halname = signal_config["halname"]
                if direction in {"output", "inout"} and name == halname:
                    signal_config["value"] = value

    def interface_value_set(self, name, value):
        for plugin_instance in self.plugin_instances:
            for interface_name, interface_config in plugin_instance.interface_data().items():
                direction = interface_config["direction"]
                virtual = interface_config.get("virtual", False)
                if virtual:
                    # swap direction vor virt signals
                    if direction == "input":
                        direction = "output"
                    else:
                        direction = "input"
                variable = interface_config["variable"]
                if direction in {"output", "inout"} and name == variable:
                    interface_config["value"] = value

    def haldata(self):
        haldata = {}
        for plugin_instance in self.plugin_instances:
            haldata[plugin_instance] = {
                "input": {},
                "output": {},
                "inout": {},
            }
            for signal_name, signal_config in plugin_instance.signals().items():
                direction = signal_config["direction"]
                virtual = signal_config.get("virtual", False)
                if virtual:
                    # swap direction vor virt signals
                    if direction == "input":
                        direction = "output"
                    else:
                        direction = "input"
                halname = signal_config["halname"]
                haldata[plugin_instance][direction][halname] = signal_config

        return haldata

    def txdata_get(self):
        txdata = [0] * self.buffer_bytes
        txdata[0] = 0x74
        txdata[1] = 0x69
        txdata[2] = 0x72
        txdata[3] = 0x77
        output_pos = self.buffer_size - self.header_size
        # convert signals to interface variables
        for plugin_instance in self.plugin_instances:
            plugin_instance.convert2interface()
        # set buffer

        if self.multiplexed_output:
            mpx_value = 0
            mpxid = 0
            for size, plugin_instance, data_name, data_config in self.get_interface_data():
                multiplexed = data_config.get("multiplexed", False)
                if not multiplexed:
                    continue
                variable_size = data_config["size"]
                value = data_config["value"]
                if data_config["direction"] in {"output"}:
                    if self.multiplexed_output_id == mpxid:
                        mpx_value = value
                    mpxid += 1

            variable_size = self.multiplexed_output_size
            value = mpx_value
            byte_start, byte_size, bit_offset = self.get_bype_pos(output_pos, variable_size)
            byte_start = self.buffer_bytes - 1 - byte_start
            txdata[byte_start - (byte_size - 1) : byte_start + 1] = list(pack("<i", int(value)))[0:byte_size]
            output_pos -= variable_size
            variable_size = 8
            value = self.multiplexed_output_id
            byte_start, byte_size, bit_offset = self.get_bype_pos(output_pos, variable_size)
            byte_start = self.buffer_bytes - 1 - byte_start
            txdata[byte_start - (byte_size - 1) : byte_start + 1] = list(pack("<i", int(value)))[0:byte_size]
            output_pos -= variable_size
            if self.multiplexed_output_id < self.multiplexed_output - 1:
                self.multiplexed_output_id += 1
            else:
                self.multiplexed_output_id = 0

        for size, plugin_instance, data_name, data_config in self.get_interface_data():
            multiplexed = data_config.get("multiplexed", False)
            if multiplexed:
                continue
            variable_size = data_config["size"]
            value = data_config["value"]
            if data_config["direction"] == "output" or data_config["direction"] == "inout":
                byte_start, byte_size, bit_offset = self.get_bype_pos(output_pos, variable_size)
                byte_start = self.buffer_bytes - 1 - byte_start
                if plugin_instance.TYPE == "frameio":
                    if not value:
                        value = [0] * byte_size

                    # for pv in value:
                    #    print(pv)

                    txdata[byte_start - (byte_size - 1) : byte_start + 1] = value[0:byte_size]
                elif variable_size > 1:
                    txdata[byte_start - (byte_size - 1) : byte_start + 1] = list(pack("<i", int(value)))[0:byte_size]
                else:
                    if value == 1:
                        txdata[byte_start] |= 1 << bit_offset
                output_pos -= variable_size
        return txdata

    def rxdata_set(self, rxdata):
        input_pos = self.buffer_size - self.header_size

        if self.multiplexed_input:
            variable_size = self.multiplexed_input_size
            byte_start, byte_size, bit_offset = self.get_bype_pos(input_pos, variable_size)
            byte_start = self.buffer_bytes - 1 - byte_start
            byte_pack = rxdata[byte_start - (byte_size - 1) : byte_start + 1]
            if len(byte_pack) < 4:
                byte_pack += [0] * (4 - len(byte_pack))
            self.multiplexed_input_value = unpack("<i", bytes(byte_pack))[0]
            input_pos -= variable_size
            variable_size = 8
            byte_start, byte_size, bit_offset = self.get_bype_pos(input_pos, variable_size)
            byte_start = self.buffer_bytes - 1 - byte_start
            byte_pack = rxdata[byte_start - (byte_size - 1) : byte_start + 1]
            if len(byte_pack) < 4:
                byte_pack += [0] * (4 - len(byte_pack))
            self.multiplexed_input_id = unpack("<i", bytes(byte_pack))[0]
            input_pos -= variable_size

        if self.multiplexed_input:
            mpxid = 0
            for size, plugin_instance, data_name, data_config in self.get_interface_data():
                multiplexed = data_config.get("multiplexed", False)
                if not multiplexed:
                    continue
                variable_size = data_config["size"]
                if data_config["direction"] == "input":
                    if self.multiplexed_input_id == mpxid:
                        data_config["value"] = self.multiplexed_input_value
                    mpxid += 1

        for size, plugin_instance, data_name, data_config in self.get_interface_data():
            multiplexed = data_config.get("multiplexed", False)
            if multiplexed:
                continue
            variable_size = data_config["size"]
            if data_config["direction"] == "input":
                byte_start, byte_size, bit_offset = self.get_bype_pos(input_pos, variable_size)
                byte_start = self.buffer_bytes - 1 - byte_start

                if plugin_instance.TYPE == "frameio":
                    value = rxdata[byte_start - (byte_size - 1) : byte_start + 1][0:byte_size]
                    # print(value)
                elif variable_size > 1:
                    byte_pack = rxdata[byte_start - (byte_size - 1) : byte_start + 1]
                    if len(byte_pack) < 4:
                        byte_pack += [0] * (4 - len(byte_pack))
                    value = unpack("<i", bytes(byte_pack))[0]
                else:
                    value = 1 if rxdata[byte_start] & (1 << bit_offset) else 0
                data_config["value"] = value
                input_pos -= variable_size

        # convert interface variables to signals
        for plugin_instance in self.plugin_instances:
            plugin_instance.convert2signals()

    def generator(self, preview=False):
        generate_pll = True
        if preview:
            generate_pll = False
        if self.config["toolchain"] == "platformio":
            self.generator_firmware.generator()
        else:
            self.generator_gateware.generator(generate_pll=generate_pll)
        self.generator_linuxcnc.generator()
        target = f"{self.config['output_path']}/.config.json"
        shutil.copy(self.config["json_file"], target)
