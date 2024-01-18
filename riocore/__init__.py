import copy
import glob
import importlib
import json
import os
import re
from struct import *

from .generator.Gateware import Gateware
from .generator.LinuxCNC import LinuxCNC

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
        print(plugin_name)
        self.load_plugins({"plugins": [{"type": plugin_name}]})
        plugin = self.plugin_instances[0]
        print(plugin.NAME)
        print(plugin.VERILOGS)
        print(plugin.PINDEFAULTS)
        print("")
        print(plugin.INFO)
        print("")
        print("## basic example:")
        print("```")
        print(json.dumps(plugin.basic_config(), indent=4))
        print("```")
        print("")
        print(plugin.DESCRIPTION)

    def load_plugin(self, plugin_id, plugin_config, system_setup=None):
        plugin_type = plugin_config["type"]
        if plugin_type not in self.plugin_modules:
            if os.path.isfile(f"{riocore_path}/plugins/{plugin_type}/plugin.py"):
                # print(f"loading plugin {plugin_type}")
                self.plugin_modules[plugin_type] = importlib.import_module(".plugin", f"riocore.plugins.{plugin_type}")
            elif os.path.isfile(f"{riocore_path}/plugins/{plugin_type}/{plugin_type}.v"):
                if self.plugin_builder(plugin_type, f"{riocore_path}/plugins/{plugin_type}/{plugin_type}.v", plugin_config):
                    self.plugin_modules[plugin_type] = importlib.import_module(".plugin", f"riocore.plugins.{plugin_type}")
            else:
                print(f"WARNING: plugin not found: {plugin_type}")
        if plugin_type in self.plugin_modules:
            plugin_instance = self.plugin_modules[plugin_type].Plugin(plugin_id, plugin_config, system_setup=system_setup)
            self.plugin_instances.append(plugin_instance)
            return plugin_instance

    def load_plugins(self, config, system_setup=None):
        for plugin_id, plugin_config in enumerate(config["plugins"]):
            self.load_plugin(plugin_id, plugin_config, system_setup=system_setup)
        return self.plugin_instances

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
                initfile.append("from riocore.plugins.PluginBase import PluginBase")
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
                    initfile.append('                "pullup": False,')
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
                            initfile.append(f'                "bool": True,')
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
                            initfile.append(f'        # frequency = int(self.plugin_setup.get("frequency", 100))')
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
    def __init__(self, configuration):
        plugins = Plugins()
        self.load_config(configuration)
        self.plugin_instances = plugins.load_plugins(self.config, system_setup=self.config)
        self.calc_buffersize()
        self.generator_linuxcnc = LinuxCNC(self)
        self.generator_gateware = Gateware(self)

    def get_path(self, path):
        if os.path.exists(path):
            return path
        elif os.path.exists(f"{riocore_path}/{path}"):
            return f"{riocore_path}/{path}"
        print(f"can not find path: {path}")
        exit(1)

    def load_config(self, configuration):
        project = {}
        # project["config"] = configuration
        if isinstance(configuration, str) and configuration[0] == "{":
            project = {"jdata": json.loads(configuration)}
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

        project["plugins"] = copy.deepcopy(project["jdata"].get("plugins"))
        project["board_data"] = {}

        # loading board data
        board = project["jdata"].get("boardcfg")
        if board:
            print(f"loading board setup: {board}")
            board_file = self.get_path(f"boards/{board}.json")
            bdata = open(board_file, "r").read()
            project["board_data"] = json.loads(bdata)
            if "name" in project["board_data"]:
                project["board"] = project["board_data"]["name"]
            for key, value in project["board_data"].items():
                if key not in project["jdata"]:
                    project["jdata"][key] = value

        # loading modules
        project["modules"] = {}
        modules_path = self.get_path(f"modules")
        for path in glob.glob(f"{modules_path}/*.json"):
            module = path.split("/")[-1].split(".")[0]
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
                module = modulesetup.get("module")
                ssetup = modulesetup.get("setup")
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
                            # rewrite pins
                            for pname, pin in ssetup[msetup_name].get("pins", {}).items():
                                realpin = spins[pin["pin"]]
                                ssetup[msetup_name]["pins"][pname]["pin"] = realpin
                            module_data["plugins"][jn] = ssetup[msetup_name]
                        # merge into jdata
                        project["plugins"] += module_data["plugins"]
                else:
                    print(f"ERROR: module {module} not found")
                    exit(1)

        self.config = project
        self.config["speed"] = int(project["jdata"]["clock"]["speed"])
        self.config["osc_clock"] = int(project["jdata"]["clock"].get("osc_clock", 0))
        self.config["sysclk_pin"] = project["jdata"]["clock"]["pin"]
        self.config["error_pin"] = project["jdata"].get("error", {}).get("pin")
        self.config["output_path"] = f"Output/{project['jdata']['name']}"
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
                        self.multiplexed_input_size = max(self.multiplexed_input_size, variable_size)
                    else:
                        self.input_size += variable_size
                elif data_config["direction"] == "output":
                    if multiplexed:
                        self.multiplexed_output += 1
                        self.multiplexed_output_size = max(self.multiplexed_output_size, variable_size)
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
        for ppath in glob.glob(f"{os.path.dirname(__file__)}/interfaces/*/*.py"):
            plugin = os.path.basename(os.path.dirname(ppath))
            interface = importlib.import_module(f".interface", f"riocore.interfaces.{plugin}")
            if interface.Interface.check(cstr):
                print(f"connection via: {plugin}")
                connection = interface.Interface(cstr)
                break

        self.connection = connection
        return connection

    def transfare(self, data):
        return self.connection.transfare(data)

    def signal_value_set(self, name, value):
        for plugin_instance in self.plugin_instances:
            for signal_name, signal_config in plugin_instance.signals().items():
                direction = signal_config["direction"]
                halname = signal_config["halname"]
                if direction == "output" and name == halname:
                    signal_config["value"] = value

    def interface_value_set(self, name, value):
        for plugin_instance in self.plugin_instances:
            for interface_name, interface_config in plugin_instance.interface_data().items():
                direction = interface_config["direction"]
                variable = interface_config["variable"]
                if direction == "output" and name == variable:
                    interface_config["value"] = value

    def haldata(self):
        haldata = {}
        for plugin_instance in self.plugin_instances:
            haldata[plugin_instance] = {
                "input": {},
                "output": {},
            }
            for signal_name, signal_config in plugin_instance.signals().items():
                direction = signal_config["direction"]
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
            for (size, plugin_instance, data_name, data_config) in self.get_interface_data():
                multiplexed = data_config.get("multiplexed", False)
                if not multiplexed:
                    continue
                variable_name = data_config["variable"]
                variable_size = data_config["size"]
                value = data_config["value"]
                if data_config["direction"] == "output":
                    if self.multiplexed_output_id == mpxid:
                        mpx_value = value
                    mpxid += 1

            variable_name = "MULTIPLEXER_OUTPUT_VALUE"
            variable_size = self.multiplexed_output_size
            value = mpx_value
            byte_start, byte_size, bit_offset = self.get_bype_pos(output_pos, variable_size)
            byte_start = self.buffer_bytes - 1 - byte_start
            txdata[byte_start - (byte_size - 1) : byte_start + 1] = joint = list(pack("<i", int(value)))[0:byte_size]
            output_pos -= variable_size

            variable_name = "MULTIPLEXER_OUTPUT_ID"
            variable_size = 8
            value = self.multiplexed_output_id
            byte_start, byte_size, bit_offset = self.get_bype_pos(output_pos, variable_size)
            byte_start = self.buffer_bytes - 1 - byte_start
            txdata[byte_start - (byte_size - 1) : byte_start + 1] = joint = list(pack("<i", int(value)))[0:byte_size]
            output_pos -= variable_size
            if self.multiplexed_output_id < self.multiplexed_output - 1:
                self.multiplexed_output_id += 1
            else:
                self.multiplexed_output_id = 0

        for (size, plugin_instance, data_name, data_config) in self.get_interface_data():
            multiplexed = data_config.get("multiplexed", False)
            if multiplexed:
                continue
            variable_name = data_config["variable"]
            variable_size = data_config["size"]
            value = data_config["value"]
            if data_config["direction"] == "output":
                byte_start, byte_size, bit_offset = self.get_bype_pos(output_pos, variable_size)
                byte_start = self.buffer_bytes - 1 - byte_start
                if variable_size > 1:
                    txdata[byte_start - (byte_size - 1) : byte_start + 1] = joint = list(pack("<i", int(value)))[0:byte_size]
                else:
                    if value == 1:
                        txdata[byte_start] |= 1 << bit_offset
                output_pos -= variable_size
        return txdata

    def rxdata_set(self, rxdata):
        input_pos = self.buffer_size - self.header_size

        if self.multiplexed_input:
            variable_name = "MULTIPLEXER_INPUT_VALUE"
            variable_size = self.multiplexed_input_size
            byte_start, byte_size, bit_offset = self.get_bype_pos(input_pos, variable_size)
            byte_start = self.buffer_bytes - 1 - byte_start
            byte_pack = rxdata[byte_start - (byte_size - 1) : byte_start + 1]
            if len(byte_pack) < 4:
                byte_pack += [0] * (4 - len(byte_pack))
            self.multiplexed_input_value = unpack("<i", bytes(byte_pack))[0]
            input_pos -= variable_size

            variable_name = "MULTIPLEXER_INPUT_ID"
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
            for (size, plugin_instance, data_name, data_config) in self.get_interface_data():
                multiplexed = data_config.get("multiplexed", False)
                if not multiplexed:
                    continue
                variable_name = data_config["variable"]
                variable_size = data_config["size"]
                if data_config["direction"] == "input":
                    if self.multiplexed_input_id == mpxid:
                        data_config["value"] = self.multiplexed_input_value
                    mpxid += 1

        for (size, plugin_instance, data_name, data_config) in self.get_interface_data():
            multiplexed = data_config.get("multiplexed", False)
            if multiplexed:
                continue
            variable_name = data_config["variable"]
            variable_size = data_config["size"]
            if data_config["direction"] == "input":
                byte_start, byte_size, bit_offset = self.get_bype_pos(input_pos, variable_size)
                byte_start = self.buffer_bytes - 1 - byte_start
                if variable_size > 1:
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

    def generator(self):
        self.generator_gateware.generator()
        self.generator_linuxcnc.generator()
