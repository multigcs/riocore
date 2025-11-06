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

# from .generator.EtherCat import EtherCat
from .generator.Simulator import Simulator
from .generator.LinuxCNC import LinuxCNC

from riocore.generator.rosbridge import rosbridge
from riocore.generator.mqttbridge import mqttbridge
from riocore.generator.easycat import easycat
from riocore.generator.jslib import jslib
from riocore.generator.documentation import documentation

riocore_path = os.path.dirname(__file__)

loginfo = []


def log(text):
    if text in loginfo:
        return
    print(text)
    loginfo.append(text)


def log_get(lines=100):
    return "\n".join(loginfo[:lines])


def log_clear():
    loginfo.clear()


class Plugins:
    def __init__(self, node_types=False):
        self.node_types = node_types
        self.plugin_modules = {}
        self.plugin_instances = []

    def list(self, splitted=False):
        plugins = []
        for plugin_path in sorted(glob.glob(os.path.join(riocore_path, "plugins", "*", "plugin.py"))):
            plugin_name = os.path.basename(os.path.dirname(plugin_path))
            if splitted is True:
                self.load_plugins({"plugins": [{"type": plugin_name}]})
                plugin_instance = self.plugin_instances[-1]
                description = plugin_instance.DESCRIPTION
                info = plugin_instance.INFO
                keywords = plugin_instance.KEYWORDS
                if "node_type" in plugin_instance.OPTIONS:
                    option_data = plugin_instance.OPTIONS["node_type"]
                    for option in option_data["options"]:
                        plugin_instance.plugin_setup["node_type"] = option
                        plugin_instance.setup()
                        description = copy.deepcopy(plugin_instance.DESCRIPTION)
                        info = copy.deepcopy(plugin_instance.INFO)
                        keywords = copy.deepcopy(plugin_instance.KEYWORDS) + option
                        plugins.append({"name": f"{plugin_name} {option}", "path": plugin_path, "description": description, "info": info, "keywords": keywords, "ptype": plugin_instance.PLUGIN_TYPE})
                else:
                    plugins.append({"name": plugin_name, "path": plugin_path, "description": description, "info": info, "keywords": keywords, "ptype": plugin_instance.PLUGIN_TYPE})
            else:
                plugins.append({"name": plugin_name, "path": plugin_path})
        return plugins

    def info(self, plugin_name):
        output = []
        self.load_plugins({"plugins": [{"type": plugin_name}]})
        plugin = self.plugin_instances[-1]
        plugin_path = os.path.join(riocore_path, "plugins", plugin_name)
        image_path = os.path.join(plugin_path, "image.png")

        output.append(f"# {plugin.NAME}")

        if os.path.isfile(image_path):
            output.append("")
            output.append('<img align="right" width="320" src="image.png">')
            output.append("")

        if plugin.EXPERIMENTAL:
            output.append("")
            output.append("| :warning: EXPERIMENTAL |")
            output.append("|:-----------------------|")
            output.append("")

        if plugin.INFO:
            output.append(f"**{plugin.INFO}**")
            output.append("")
        if plugin.DESCRIPTION:
            output.append(plugin.DESCRIPTION.strip())
            output.append("")
        if plugin.KEYWORDS:
            output.append(f"Keywords: {plugin.KEYWORDS}")
            output.append("")
        if plugin.URL:
            output.append(f"URL: {plugin.URL.strip()}")
            output.append("")

        if plugin.LIMITATIONS:
            output.append("## Limitations")
            for key, values in plugin.LIMITATIONS.items():
                output.append(f"* {key}: {', '.join(values)}")
            output.append("")

        if plugin.GRAPH:
            output.append("```mermaid")
            output.append(plugin.GRAPH.strip())
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
        output.append("## Basic-Example:")
        output.append("```")
        output.append(json.dumps(plugin.basic_config(), indent=4))
        output.append("```")
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

    def load_plugin(self, plugin_id, plugin_config, system_setup=None, subfix=None):
        try:
            plugin_type = plugin_config["type"]
            if plugin_type not in self.plugin_modules:
                if os.path.isfile(os.path.join(riocore_path, "plugins", plugin_type, "plugin.py")):
                    self.plugin_modules[plugin_type] = importlib.import_module(".plugin", f"riocore.plugins.{plugin_type}")
                elif os.path.isfile(os.path.join(riocore_path, "plugins", plugin_type, f"{plugin_type}.v")):
                    if self.plugin_builder(plugin_type, os.path.join(riocore_path, "plugins", plugin_type, f"{plugin_type}.v"), plugin_config):
                        self.plugin_modules[plugin_type] = importlib.import_module(".plugin", f"riocore.plugins.{plugin_type}")
                elif not plugin_type or plugin_type[0] != "_":
                    ppath = os.path.join(riocore_path, "plugins", plugin_type, "plugin.py")
                    log(f"WARNING: plugin not found: {plugin_type}: {ppath}")

            if plugin_type in self.plugin_modules:
                plugin_instance = self.plugin_modules[plugin_type].Plugin(plugin_id, plugin_config, system_setup=system_setup, subfix=subfix)
                plugin_instance.setup_object = plugin_config
                for pin_name, pin_config in plugin_instance.pins().items():
                    if "pin" in pin_config and pin_config["pin"] and not pin_config["pin"].startswith("EXPANSION"):
                        if pin_config["pin"] == "" or pin_config["pin"] is None:
                            log(f"WARNING: pin '{pin_name}' of '{plugin_instance.instances_name}' is not set / removed")
                            del pin_config["pin"]

                for option_name, option_data in plugin_instance.OPTIONS.items():
                    if option_name == "is_joint" and option_name not in plugin_instance.plugin_setup and option_data.get("default"):
                        plugin_instance.plugin_setup[option_name] = option_data.get("default")

                self.plugin_instances.append(plugin_instance)

                return plugin_instance
        except Exception:
            log(f"ERROR: loading plugin: {plugin_id} / {plugin_config}")
            log("##################################")
            traceback.print_exc(file=sys.stdout)
            log("##################################")
            return False
        return True

    def load_plugins(self, config, system_setup=None):
        if config["plugins"]:
            for plugin_id, plugin_config in enumerate(config["plugins"]):
                if not self.load_plugin(plugin_id, plugin_config, system_setup=system_setup):
                    exit(1)
            return self.plugin_instances
        return []

    def testbench_builder(self, plugin_type, plugin_instance):
        log(f"try to build testbench for {plugin_type}")

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
                        tbfile.append(f"    reg signed [{size - 1}:0] {data_name} = {size}'d0;")
                    else:
                        if data_name == "enable":
                            tbfile.append(f"    reg {data_name} = 1;")
                        else:
                            tbfile.append(f"    reg {data_name} = 0;")
                else:
                    if size > 1:
                        tbfile.append(f"    wire signed [{size - 1}:0] {data_name};")
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
            open(os.path.join(riocore_path, "plugins", plugin_type, "testb.v"), "w").write("\n".join(tbfile))

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
                    gtkwfile.append(f"testb.{data_name}[{size - 1}:0]")
                else:
                    gtkwfile.append(f"testb.{data_name}")
                pn += 1

            gtkwfile.append("")
            open(os.path.join(riocore_path, "plugins", plugin_type, "testb.gtkw"), "w").write("\n".join(gtkwfile))

            makefile = []
            makefile.append("")
            makefile.append("all: testb")
            makefile.append("")
            makefile.append("testb:")
            makefile.append(f"	iverilog -Wall -o testb.out testb.v {plugin_type}.v")
            makefile.append("	vvp testb.out")
            makefile.append("	test -e testb.gtkw && gtkwave testb.gtkw || gtkwave testb.vcd")
            makefile.append("")
            makefile.append("clean:")
            makefile.append("	rm -rf testb.out testb.vcd")
            makefile.append("")
            open(os.path.join(riocore_path, "plugins", plugin_type, "Makefile"), "w").write("\n".join(makefile))

            log(f"(cd {os.path.join(riocore_path, 'plugins', plugin_type)} ; make)")

            return True

        return False

    def plugin_builder(self, plugin_name, verilog_file, plugin_config):
        log(f"try to autoload plugin from {plugin_name}.v")
        verilog_data = open(verilog_file, "r").read()
        x = re.search(r"(module\s+)(?P<name>[a-z0-9_]+)\s+(?P<parameters>#\([^\).]*\))?\s*(?P<arguments>\([^\).]*\));", verilog_data)
        if x is not None:
            if plugin_name != x.group("name"):
                log(f"ERROR: wrong toplevel name: {x.group('name')}, needs: {plugin_name}")
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
                            log(f"WARNING: can not parse size: {part}, using 32")
                            argument_size = 32
                    elif part in {"reg", "wire", "=", "signed", "unsigned"}:
                        pass
                    elif part in {"input", "output", "inout"}:
                        argument_direction = part
                    elif not argument_name:
                        argument_name = part

                log(argument_name, argument_size, argument_name in plugin_config.get("pins", {}))

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
                log("FAILED: can not find clock pin")
            elif not pindefaults:
                log("FAILED: can not find io pin's")
            elif not interface and not signals and not is_interface:
                log("FAILED: can not find interface/signals")
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
                    initfile.append(f'                "direction": "{pin_setup["direction"]}",')
                    initfile.append('                "invert": False,')
                    initfile.append('                "pull": None,')
                    initfile.append("            },")
                initfile.append("        }")
                if interface:
                    initfile.append("        self.INTERFACE = {")
                    for interface_name, interface_setup in interface.items():
                        initfile.append(f'            "{interface_name}": {{')
                        initfile.append(f'                "size": {interface_setup["size"]},')
                        initfile.append(f'                "direction": "{interface_setup["direction"]}",')
                        initfile.append("            },")
                    initfile.append("        }")
                if signals:
                    initfile.append("        self.SIGNALS = {")
                    for signal_name, signal_setup in signals.items():
                        initfile.append(f'            "{signal_name}": {{')
                        initfile.append(f'                "direction": "{signal_setup["direction"]}",')
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
                        initfile.append(f'        # instance_parameter["{parameter_name}"] = self.plugin_setup.get("{parameter_name.lower()}", "{parameter_setup["default"]}")')
                    initfile.append("        return instances")
                    initfile.append("")
                if os.path.isfile(os.path.join(riocore_path, "plugins", plugin_name, "plugin.py")):
                    log(f"WARNING: file allready exsits: {os.path.join(riocore_path, 'plugins', plugin_name, 'plugin.py')}")
                    log("\n".join(initfile))
                    log("")
                else:
                    log(f"INFO: writing plugin setup to {os.path.join(riocore_path, 'plugins', plugin_name, 'plugin.py')} (please edit)")
                    open(os.path.join(riocore_path, "plugins", plugin_name, "plugin.py"), "w").write("\n".join(initfile))
                    log("")

                if plugin_config.get("init") is True:
                    log("# config example:")
                    log("    {")
                    log(f'        "type": "{plugin_name}",')
                    log('        "pins": {')
                    pn = 0
                    for pin_name, pin_setup in pindefaults.items():
                        log(f'            "{pin_name}": {{')
                        log(f'                "pin": "{pn}",')
                        log("            },")
                        pn += 1
                    log("        }")
                    log("    },")
                    log("")
                    log(".... OK")
                return True
        log(".... Failed")
        return False


class Project:
    def __init__(self, configuration, output_path=None):
        plugins = Plugins()
        self.pin_mapping = {}
        self.timestamp = 0
        self.timestamp_last = 0
        self.duration = 0
        self.load_config(configuration, output_path)
        self.plugin_instances = plugins.load_plugins(self.config, system_setup=self.config)

        for plugin_instance in self.plugin_instances:
            if hasattr(plugin_instance, "update_system_setup"):
                plugin_instance.update_system_setup(self)

        # expansion mapping after plugin load
        expansion_mapping = {}
        for plugin_instance in self.plugin_instances:
            if plugin_instance.TYPE == "expansion":
                for exp_pin in plugin_instance.expansion_inputs():
                    source = f"{plugin_instance.instances_name}:{exp_pin}"
                    expansion_mapping[source] = exp_pin
                for exp_pin in plugin_instance.expansion_outputs():
                    source = f"{plugin_instance.instances_name}:{exp_pin}"
                    expansion_mapping[source] = exp_pin
            else:
                for gpio_pin, gpio_data in plugin_instance.PINDEFAULTS.items():
                    if "pin" not in gpio_data:
                        continue
                    source = f"{plugin_instance.instances_name}:{gpio_pin}"
                    self.pin_mapping[source] = gpio_data["pin"]

        # breakout plugins
        for n in range(5):
            for plugin_instance in self.plugin_instances:
                for gpio_pin, gpio_data in plugin_instance.PINDEFAULTS.items():
                    if "source" in gpio_data:
                        source = f"{plugin_instance.instances_name}:{gpio_pin}"
                        target = plugin_instance.PINDEFAULTS[gpio_data["source"]]
                        if target:
                            target_pin = plugin_instance.plugin_setup.get("pins", {}).get(gpio_data["source"], {}).get("pin")
                            self.pin_mapping[source] = self.pin_mapping.get(target_pin, target_pin)

        # cleaning slot-pins (breakout-pins)
        for plugin_instance in self.plugin_instances:
            for pin_name in list(plugin_instance.PINDEFAULTS):
                ptype = plugin_instance.PINDEFAULTS[pin_name].get("type", [])
                if "BREAKOUT" in ptype:
                    del plugin_instance.PINDEFAULTS[pin_name]

        # update plugin pins
        for plugin in self.config["plugins"]:
            for pin_name, pin_data in plugin.get("pins", {}).items():
                if "pin" in pin_data and pin_data["pin"] in self.pin_mapping:
                    pin_data["pin"] = self.pin_mapping[pin_data["pin"]]

        self.calc_buffersize()
        self.generator_linuxcnc = LinuxCNC(self)
        self.generator_simulator = Simulator(self)

        # check names
        varnames = {}
        for plugin_instance in self.plugin_instances:
            for signal_name, signal_config in plugin_instance.signals().items():
                varname = signal_config["varname"]
                if varname not in varnames:
                    varnames[varname] = plugin_instance.instances_name
                else:
                    log(f"ERROR: varname allready exist: {varname} ({plugin_instance.instances_name} / {varnames[varname]})")

    def info(self):
        jdata = self.config["jdata"]
        name = jdata.get("name")
        output = [f"RIO - {name}"]
        output.append("")
        for name in ("description", "gui", "protocol"):
            value = jdata.get(name)
            if value:
                output.append(f"{name.title()}: {value}")
        output.append(f"Configuration: {self.config['json_file']}")
        output.append("")

        protocol = jdata.get("protocol", "SPI")
        if protocol == "UDP":
            ip = "192.168.10.194"
            port = 2390
            for plugin_instance in self.plugin_instances:
                if plugin_instance.TYPE == "interface":
                    ip = plugin_instance.plugin_setup.get("ip", plugin_instance.option_default("ip", ip))
                    port = plugin_instance.plugin_setup.get("port", plugin_instance.option_default("port", port))
            ip = self.config["jdata"].get("ip", ip)
            port = self.config["jdata"].get("port", port)
            dst_port = self.config["jdata"].get("dst_port", port)
            output.append("UDP-Configuration:")
            output.append(f"  Target-IP: {ip}")
            output.append(f"  Target-Port: {dst_port}")
            output.append("")

        output.append("Plugins:")
        plugins = {}
        for plugin in self.config.get("plugins", []):
            ptype = plugin["type"]
            if ptype not in plugins:
                plugins[ptype] = 0
            plugins[ptype] += 1
        for plugin, num in plugins.items():
            output.append(f"  {plugin} ({num}x)")
        output.append("")

        output.append("")
        return "\n".join(output)

    def get_path(self, path):
        if os.path.exists(path):
            return path
        elif os.path.exists(os.path.join(riocore_path, path)):
            return os.path.join(riocore_path, path)
        log(f"path not found: {path} or {os.path.join(riocore_path, path)}")
        exit(1)

    def load_config(self, configuration, output_path=None):
        project = {}
        project["json_path"] = ""

        if output_path is None:
            output_path = "Output"

        # project["config"] = configuration
        if isinstance(configuration, dict):
            project = {"jdata": configuration}
            project["json_file"] = None
            project["json_path"] = ""
        elif isinstance(configuration, str) and configuration[0] == "{":
            project = {"jdata": json.loads(configuration)}
            project["json_file"] = None
            project["json_path"] = ""
        else:
            if not os.path.isfile(configuration):
                log("")
                log(f"this is not a file: {configuration}")
                log("")
                exit(1)
            try:
                with open(configuration, "r") as f:
                    data = f.read()
            except IOError as err:
                log("")
                log(err)
                log("")
                exit(1)

            try:
                project["jdata_str"] = data
                project["jdata"] = json.loads(data)
            except ValueError as err:
                log("")
                log(f"JSON error: {err}")
                log("please check your json syntax")
                log("")
                exit(1)
            project["json_file"] = configuration
            project["json_path"] = os.path.dirname(configuration)

        project["plugins"] = copy.deepcopy(project["jdata"].get("plugins", []))

        self.pin_mapping = {}

        # loading modules
        project["modules"] = {}
        modules_path = self.get_path("modules")
        for path in sorted(glob.glob(os.path.join(modules_path, "*", "module.json"))):
            module = path.split(os.sep)[-2]
            mdata = open(path, "r").read()
            project["modules"][module] = json.loads(mdata)

        self.config = project
        self.config["pin_mapping"] = self.pin_mapping
        self.config["output_path"] = os.path.join(output_path, project["jdata"]["name"])
        self.config["name"] = project["jdata"]["name"]
        self.config["json_path"] = project["json_path"]

    def setup_merge(self, setup, defaults):
        for key, value in defaults.items():
            if key not in setup:
                setup[key] = copy.deepcopy(value)
            elif isinstance(value, dict):
                self.setup_merge(setup[key], value)

    def calc_buffersize(self):
        self.timestamp_size = 32
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
            if plugin_instance.PLUGIN_TYPE != "gateware":
                continue
            for data_name, data_config in plugin_instance.interface_data().items():
                self.interface_sizes.add(data_config["size"])
                variable_size = data_config["size"]
                multiplexed = data_config.get("multiplexed", False)
                expansion = data_config.get("expansion", False)
                if expansion:
                    continue
                if data_config["direction"] == "input":
                    if not data_config.get("expansion"):
                        if multiplexed:
                            self.multiplexed_input += 1
                            self.multiplexed_input_size = (max(self.multiplexed_input_size, variable_size) + 7) // 8 * 8
                            if self.multiplexed_input_size < 8:
                                self.multiplexed_input_size = 8
                        else:
                            self.input_size += variable_size
                elif data_config["direction"] == "output":
                    if not data_config.get("expansion"):
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

        self.input_size = self.input_size + self.header_size + self.timestamp_size
        self.output_size = self.output_size + self.header_size
        self.buffer_size = (max(self.input_size, self.output_size) + 7) // 8 * 8
        self.buffer_bytes = self.buffer_size // 8
        self.config["buffer_size"] = self.buffer_size

        # log("# PC->FPGA", self.output_size)
        # log("# FPGA->PC", self.input_size)
        # log("# MAX", self.buffer_size)

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
                if plugin_instance.PLUGIN_TYPE != "gateware":
                    continue
                for data_name, data_config in plugin_instance.interface_data().items():
                    if data_config["size"] == size:
                        interface_data.append([size, plugin_instance, data_name, data_config])
        return interface_data

    def get_signal_data(self):
        signal_data = []
        for plugin_instance in self.plugin_instances:
            for signal_name, signal_config in plugin_instance.signals().items():
                signal_data.append([plugin_instance, signal_name, signal_config])
        return signal_data

    def connect(self, cstr):
        connection = None
        for ppath in sorted(glob.glob(os.path.join(os.path.dirname(__file__), "interfaces", "*", "*.py"))):
            plugin = os.path.basename(os.path.dirname(ppath))
            interface = importlib.import_module(".interface", f"riocore.interfaces.{plugin}")
            if interface.Interface.check(cstr):
                log(f"connection via: {plugin}")
                connection = interface.Interface(cstr)
                break

        if connection is None:
            log(f"ERROR: no interface found for connection-string: {cstr}")
            exit(1)
        self.connection = connection
        return connection

    def transfare(self, data):
        return self.connection.transfare(data)

    def signal_value_set(self, name, value):
        for plugin_instance in self.plugin_instances:
            if plugin_instance.PLUGIN_TYPE != "gateware":
                continue
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
            if plugin_instance.PLUGIN_TYPE != "gateware":
                continue
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
                    # swap direction for virt signals
                    if direction == "input":
                        direction = "output"
                    else:
                        direction = "input"
                halname = signal_config["halname"]
                haldata[plugin_instance][direction][halname] = signal_config

        return haldata

    def txdata_get(self):
        # send from pc to fpga
        txdata = [0] * self.buffer_bytes
        txdata[0] = 0x74
        txdata[1] = 0x69
        txdata[2] = 0x72
        txdata[3] = 0x77
        output_pos = self.buffer_size - self.header_size
        # convert signals to interface variables
        for plugin_instance in self.plugin_instances:
            if plugin_instance.PLUGIN_TYPE != "gateware":
                continue
            plugin_instance.convert2interface()

        if self.multiplexed_output:
            mpx_value = 0
            mpxid = 0
            for size, plugin_instance, data_name, data_config in self.get_interface_data():
                expansion = data_config.get("expansion", False)
                if expansion:
                    continue
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
            expansion = data_config.get("expansion", False)
            if expansion:
                continue
            multiplexed = data_config.get("multiplexed", False)
            if multiplexed:
                continue
            variable_size = data_config["size"]
            is_float = data_config.get("is_float", False)
            value = data_config["value"]
            if data_config["direction"] == "output" or data_config["direction"] == "inout":
                byte_start, byte_size, bit_offset = self.get_bype_pos(output_pos, variable_size)
                byte_start = self.buffer_bytes - 1 - byte_start
                if plugin_instance.TYPE == "frameio":
                    if not value:
                        value = [0] * byte_size
                    txdata[byte_start - (byte_size - 1) : byte_start + 1] = value[0:byte_size]
                elif variable_size >= 8:
                    if is_float:
                        txdata[byte_start - (byte_size - 1) : byte_start + 1] = list(pack("<f", int(value)))[0:byte_size]
                    else:
                        txdata[byte_start - (byte_size - 1) : byte_start + 1] = list(pack("<i", int(value)))[0:byte_size]
                elif variable_size > 1:
                    for bit in range(variable_size - 1, -1, -1):
                        if value & (1 << bit):
                            txdata[byte_start] |= 1 << (bit_offset + bit)
                else:
                    if value == 1:
                        txdata[byte_start] |= 1 << bit_offset
                output_pos -= variable_size
        return txdata

    def rxdata_set(self, rxdata):
        if not rxdata:
            return
        input_pos = self.buffer_size - self.header_size

        # get timestamp from FPGA
        variable_size = self.timestamp_size
        byte_start, byte_size, bit_offset = self.get_bype_pos(input_pos, variable_size)
        byte_start = self.buffer_bytes - 1 - byte_start
        byte_pack = rxdata[byte_start - (byte_size - 1) : byte_start + 1]
        self.timestamp_last = self.timestamp
        self.timestamp = unpack("<I", bytes(byte_pack))[0] / self.config["speed"]
        self.duration = self.timestamp - self.timestamp_last
        input_pos -= variable_size

        if self.multiplexed_input:
            variable_size = self.multiplexed_input_size
            byte_start, byte_size, bit_offset = self.get_bype_pos(input_pos, variable_size)
            byte_start = self.buffer_bytes - 1 - byte_start
            byte_pack = rxdata[byte_start - (byte_size - 1) : byte_start + 1]
            if len(byte_pack) < 4:
                byte_pack += [0] * (4 - len(byte_pack))
            if byte_size == 8:
                self.multiplexed_input_value = unpack("<d", bytes(byte_pack))[0]
            else:
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

            # set mpx value
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
            expansion = data_config.get("expansion", False)
            if expansion:
                continue
            multiplexed = data_config.get("multiplexed", False)
            if multiplexed:
                continue
            variable_size = data_config["size"]
            is_float = data_config.get("is_float", False)

            if data_config["direction"] == "input":
                byte_start, byte_size, bit_offset = self.get_bype_pos(input_pos, variable_size)
                byte_start = self.buffer_bytes - 1 - byte_start

                if plugin_instance.TYPE == "frameio":
                    value = rxdata[byte_start - (byte_size - 1) : byte_start + 1][0:byte_size]
                    # log(value)
                elif variable_size > 1:
                    byte_pack = rxdata[byte_start - (byte_size - 1) : byte_start + 1]
                    if len(byte_pack) < 4:
                        byte_pack += [0] * (4 - len(byte_pack))
                    if is_float:
                        value = unpack("<f", bytes(byte_pack))[0]
                    else:
                        if variable_size == 4:
                            value = unpack("<B", bytes([byte_pack[0] >> 4]))[0]
                        else:
                            value = unpack("<i", bytes(byte_pack))[0]
                else:
                    value = 1 if rxdata[byte_start] & (1 << bit_offset) else 0
                data_config["value"] = value
                input_pos -= variable_size

        for size, plugin_instance, data_name, data_config in self.get_interface_data():
            plugin_instance.timestamp = self.timestamp
            plugin_instance.duration = self.duration

        # convert interface variables to signals
        for plugin_instance in self.plugin_instances:
            if plugin_instance.PLUGIN_TYPE != "gateware":
                continue
            plugin_instance.convert2signals()

    def generator(self, preview=False):
        protocol = self.config["jdata"].get("protocol", "SPI")
        self.generator_linuxcnc.generator(preview=preview)

        if not preview:
            if protocol == "UDP":
                self.generator_simulator.generator()
            if protocol == "ETHERCAT":
                easycat(self)
            else:
                rosbridge(self)
                mqttbridge(self)
                jslib(self)
        documentation(self)

        if self.config["json_file"]:
            target = os.path.join(self.config["output_path"], ".config.json")
            shutil.copy(self.config["json_file"], target)
