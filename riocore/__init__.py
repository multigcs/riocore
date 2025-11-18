import copy
import glob
import importlib
import json
import os
import re
import shutil
import sys
import traceback

from .generator.LinuxCNC import LinuxCNC
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
            plugin_id = 0
            for plugin_config in list(config["plugins"]):
                plugin_instance = self.load_plugin(plugin_id, plugin_config, system_setup=system_setup)
                if not plugin_instance:
                    exit(1)
                plugin_id += 1

                # adding sub-plugins
                if hasattr(plugin_instance, "SUB_PLUGINS"):
                    for sub_plugin_config in plugin_instance.SUB_PLUGINS:
                        # update options
                        for key, value in plugin_config.get("sub", {}).get(sub_plugin_config["uid"], {}).items():
                            sub_plugin_config[key] = value

                        config["plugins"].append(sub_plugin_config)
                        sub_plugin_config["parent"] = plugin_instance
                        sub_plugin_instance = self.load_plugin(plugin_id, sub_plugin_config, system_setup=system_setup)
                        if not sub_plugin_instance:
                            exit(1)
                        for pin_name, pin_data in sub_plugin_instance.plugin_setup.get("pins", {}).items():
                            pin_data["pin"] = f"{plugin_config['uid']}:{pin_data['pin']}"
                        plugin_id += 1

            return self.plugin_instances
        return []

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

        for n in range(5):
            # breakout plugins
            for plugin_instance in self.plugin_instances:
                for gpio_pin, gpio_data in plugin_instance.PINDEFAULTS.items():
                    if "source" in gpio_data:
                        source = f"{plugin_instance.instances_name}:{gpio_pin}"
                        if gpio_data["source"] not in plugin_instance.PINDEFAULTS:
                            continue
                        target = plugin_instance.PINDEFAULTS[gpio_data["source"]]
                        if target:
                            target_pin = plugin_instance.plugin_setup.get("pins", {}).get(gpio_data["source"], {}).get("pin")
                            self.pin_mapping[source] = self.pin_mapping.get(target_pin, target_pin)

        for plugin_instance in self.plugin_instances:
            for gpio_pin, gpio_data in plugin_instance.PINDEFAULTS.items():
                target = gpio_data.get("pin")
                if target:
                    source = f"{plugin_instance.instances_name}:{gpio_pin}"
                    self.pin_mapping[source] = target

        for n in range(5):
            # cleaning slot-pins (breakout-pins)
            for plugin_instance in self.plugin_instances:
                for pin_name in list(plugin_instance.PINDEFAULTS):
                    if pin_name not in plugin_instance.PINDEFAULTS:
                        continue
                    ptype = plugin_instance.PINDEFAULTS[pin_name].get("type", [])
                    if "BREAKOUT" in ptype:
                        del plugin_instance.PINDEFAULTS[pin_name]

        # update plugin pins
        for n in range(5):
            for plugin in self.config["plugins"]:
                for pin_name, pin_data in plugin.get("pins", {}).items():
                    if "pin" in pin_data and pin_data["pin"] in self.pin_mapping:
                        pin_data["pin"] = self.pin_mapping[pin_data["pin"]]

        self.generator_linuxcnc = LinuxCNC(self)

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

    def generator(self, preview=False):
        self.generator_linuxcnc.generator(preview=preview)
        documentation(self)

        if self.config["json_file"]:
            target = os.path.join(self.config["output_path"], ".config.json")
            shutil.copy(self.config["json_file"], target)
