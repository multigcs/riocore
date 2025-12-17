import os
import stat

from .cbase import cbase

riocore_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))


class pylib(cbase):
    filename_functions = "pylib_functions.c"
    rtapi_mode = False
    typemap = {
        "float": "float",
        "bool": "bool",
        "s32": "int32_t",
        "u32": "uint32_t",
    }
    printf = "printf"
    prefix = "/rio"
    header_list = [
        "time.h",
        "unistd.h",
        "stdint.h",
        "stdlib.h",
        "stdbool.h",
        "stdio.h",
        "string.h",
        "math.h",
        "sys/mman.h",
        "errno.h",
    ]
    module_info = {
        "AUTHOR": "Oliver Dippel",
        "DESCRIPTION": "Driver for RIO FPGA boards",
        "LICENSE": "GPL v2",
    }

    def __init__(self, project, instance):
        self.project = project
        self.instance = instance
        self.prefix = instance.hal_prefix
        self.pylib_path = os.path.join(self.project.config["output_path"], "PYLIB", instance.instances_name)
        os.makedirs(self.pylib_path, exist_ok=True)

        # c-libs
        open(os.path.join(self.pylib_path, "rio.h"), "w").write("\n".join(self.mainh()))
        open(os.path.join(self.pylib_path, "rio.c"), "w").write("\n".join(self.mainc(libmode=True)))

        # py-wrapper
        self.pylib_wrapper()

        # clients
        self.client_c()
        self.client_py()

        # misc
        self.pylib_page()
        self.pylib_startscript()
        self.pylib_makefile()

    def pylib_makefile(self):
        output = []
        output.append("")
        output.append("all: rioclient")
        output.append("")
        output.append("librio.so: rio.c")
        output.append("	gcc -shared -fPIC -o librio.so rio.c -I.")
        output.append("")
        output.append("rioclient: rioclient.c librio.so")
        output.append("	gcc -o rioclient rioclient.c -I. -L. -lrio")
        output.append("")
        output.append("clean:")
        output.append("	rm -rf rioclient librio.so")
        output.append("")
        open(os.path.join(self.pylib_path, "Makefile"), "w").write("\n".join(output))

    def pylib_page(self):
        output = []
        output.append("")

        for plugin_instance in self.project.plugin_instances:
            if plugin_instance.master != self.instance.instances_name and plugin_instance.gmaster != self.instance.instances_name:
                continue
            signals = plugin_instance.signals()
            if not signals:
                continue

            output.append(f"    <B>{plugin_instance.instances_name}</B>")
            output.append("    <table>")
            for signal_name, signal_config in signals.items():
                halname = signal_config["halname"]
                direction = signal_config["direction"]
                boolean = signal_config.get("bool")
                unit = signal_config.get("unit")
                description = signal_config.get("description")
                virtual = signal_config.get("virtual")
                if virtual:
                    continue
                if direction == "output":
                    vmin = signal_config.get("min", 0)
                    vmax = signal_config.get("max", 1000)
                    if boolean:
                        vmax = 1
                    output.append("      <tr>")
                    if description:
                        output.append(f'        <td><div class="tooltip">{signal_name}<span class="tooltiptext">{description}</span></div>:</td>')
                    else:
                        output.append(f"        <td>{signal_name}</td>")
                    if boolean:
                        output.append(f'        <td><input type="checkbox" id="{self.pylibname(halname)}" /></td>')
                    else:
                        output.append(f'        <td><b id="{self.pylibname(halname)}_fb">0</b></td>')
                        if unit:
                            output.append(f"        <td>{unit}</td>")
                        output.append(f'        <td><input type="range" min="{vmin}" max="{vmax}" id="{self.pylibname(halname)}" value="0" /></td>')
                    if vmin < 0:
                        output.append(f'        <td><button onclick="document.getElementById(\'{self.pylibname(halname)}\').value = 0;" id="{self.pylibname(halname)}_zero" type="button">0</button></td>')
                    output.append("      </tr>")
                elif direction == "input":
                    output.append("      <tr>")
                    if description:
                        output.append(f'        <td><div class="tooltip">{signal_name}<span class="tooltiptext">{description}</span></div>:</td>')
                    else:
                        output.append(f"        <td>{signal_name}</td>")
                    output.append(f'        <td><b id="{self.pylibname(halname)}">0</b></td>')
                    if unit:
                        output.append(f"        <td>{unit}</td>")
                    output.append("      </tr>")
            output.append("    </table>")
            output.append("        </div>")

        output.append("    </div>")

        output.append("")
        open(os.path.join(self.pylib_path, "test.html"), "w").write("\n".join(output))

    def pylib_wrapper(self):
        output = [""]
        output.append("import sys")
        output.append("import time")
        output.append("import ctypes")
        output.append("import pathlib")
        output.append("")
        output.append("class RioData(ctypes.Structure):")
        output.append("    _fields_ = [")
        output.append('      ("sys_enable", ctypes.POINTER(ctypes.c_bool)),')
        output.append('      ("sys_enable_request", ctypes.POINTER(ctypes.c_bool)),')
        output.append('      ("sys_status", ctypes.POINTER(ctypes.c_bool)),')
        output.append('      ("machine_on", ctypes.POINTER(ctypes.c_bool)),')
        output.append('      ("sys_simulation", ctypes.POINTER(ctypes.c_bool)),')
        output.append('      ("fpga_timestamp", ctypes.POINTER(ctypes.c_int)),')
        output.append('      ("duration", ctypes.POINTER(ctypes.c_float)),')
        if self.instance.gateware.multiplexed_output or self.instance.gateware.multiplexed_input:
            output.append("      # multiplexer")
        if self.instance.gateware.multiplexed_output:
            output.append('      ("MULTIPLEXER_OUTPUT_VALUE", ctypes.POINTER(ctypes.c_float)),')
            output.append('      ("MULTIPLEXER_OUTPUT_ID", ctypes.POINTER(ctypes.c_char)),')
        if self.instance.gateware.multiplexed_input:
            output.append('      ("MULTIPLEXER_INPUT_VALUE", ctypes.c_float),')
            output.append('      ("MULTIPLEXER_INPUT_ID", ctypes.c_char),')
        output.append("      # signals")
        for plugin_instance in self.project.plugin_instances:
            if plugin_instance.master != self.instance.instances_name and plugin_instance.gmaster != self.instance.instances_name:
                continue
            for signal_name, signal_config in plugin_instance.signals().items():
                varname = signal_config["varname"]
                # var_prefix = signal_config["var_prefix"]
                direction = signal_config["direction"]
                boolean = signal_config.get("bool")
                signal_source = signal_config.get("source")
                hal_type = signal_config.get("userconfig", {}).get("hal_type", signal_config.get("hal_type", "float"))
                vtype = self.typemap.get(hal_type, hal_type)
                virtual = signal_config.get("virtual")
                component = signal_config.get("component")
                if virtual and component:
                    # swap direction vor virt signals in component
                    if direction == "input":
                        direction = "output"
                    else:
                        direction = "input"
                elif virtual:
                    continue
                if not boolean:
                    output.append(f'      ("{varname}", ctypes.POINTER(ctypes.c_{vtype})),')
                    if not signal_source and not signal_config.get("helper", False):
                        if direction == "input" and hal_type == "float":
                            output.append(f'      ("{varname}_ABS", ctypes.POINTER(ctypes.c_{vtype})),')
                            output.append(f'      ("{varname}_S32", ctypes.POINTER(ctypes.c_int32)),')
                            output.append(f'      ("{varname}_U32_ABS", ctypes.POINTER(ctypes.c_uint32)),')
                        if not virtual:
                            output.append(f'      ("{varname}_SCALE", ctypes.POINTER(ctypes.c_float)),')
                            output.append(f'      ("{varname}_OFFSET", ctypes.POINTER(ctypes.c_float)),')
                else:
                    output.append(f'      ("{varname}", ctypes.POINTER(ctypes.c_bool)),')
                    if direction == "input":
                        output.append(f'      ("{varname}_not", ctypes.POINTER(ctypes.c_bool)),')
                    if signal_config.get("is_index_out"):
                        output.append(f'      ("{varname}_INDEX_RESET", ctypes.POINTER(ctypes.c_bool)),')
                        output.append(f'      ("{varname}_INDEX_WAIT", ctypes.POINTER(ctypes.c_bool)),')
        output.append("      # raw variables")
        for size, plugin_instance, data_name, data_config in self.instance.gateware.get_interface_data(self.project):
            expansion = data_config.get("expansion", False)
            if expansion:
                continue
            variable_name = data_config["variable"]
            variable_size = data_config["size"]
            is_float = data_config.get("is_float", False)
            variable_bytesize = variable_size // 8
            if plugin_instance.TYPE == "frameio":
                output.append(f'      ("{variable_name}", ctypes.c_char * {variable_bytesize}),')
            elif variable_size > 1:
                variable_size_align = 8
                for isize in (8, 16, 32, 64):
                    variable_size_align = isize
                    if isize >= variable_size:
                        break
                if is_float:
                    output.append(f'      ("{variable_name}", ctypes.c_float),')
                elif variable_size < 8:
                    output.append(f'      ("{variable_name}", ctypes.c_uint{variable_size_align}),')
                else:
                    output.append(f'      ("{variable_name}", ctypes.c_uint{variable_size_align}),')
            else:
                output.append(f'      ("{variable_name}", ctypes.c_bool),')
        output.append("    ]")
        output.append("")
        output.append("class RioWrapper():")
        output.append("    def __init__(self):")
        output.append('        libname = pathlib.Path().absolute() / "librio.so"')
        output.append("        self.rio = ctypes.CDLL(libname)")
        output.append("        self.rio.init.restype = ctypes.POINTER(RioData)")
        output.append("        p_args = list((arg.encode() for arg in sys.argv))")
        output.append("        args = (ctypes.c_char_p * len(p_args))(*p_args)")
        output.append("        self.rio_data = self.rio.init(len(args), args)")
        output.append("")
        output.append("    def rio_readwrite(self):")
        output.append("     self.rio.rio_readwrite(None, 0)")
        output.append("")
        output.append("    def data_get(self, name):")
        output.append("        var = getattr(self.rio_data.contents, name)")
        output.append('        if hasattr(var, "contents"):')
        output.append("            return var.contents.value")
        output.append("        return var")
        output.append("")
        output.append("    def data_set(self, name, value):")
        output.append("        var = getattr(self.rio_data.contents, name)")
        output.append('        if hasattr(var, "contents"):')
        output.append("            var.contents.value = value")
        output.append("        var = value")
        output.append("")
        output.append("    def data_info(self):")
        output.append("        return {")
        for plugin_instance in self.project.plugin_instances:
            if plugin_instance.master != self.instance.instances_name and plugin_instance.gmaster != self.instance.instances_name:
                continue
            for signal_name, signal_config in plugin_instance.signals().items():
                varname = signal_config["varname"]
                halname = signal_config["halname"]
                direction = signal_config["direction"]
                netname = signal_config["netname"]
                boolean = signal_config.get("bool")
                signal_source = signal_config.get("source")
                hal_type = signal_config.get("userconfig", {}).get("hal_type", signal_config.get("hal_type", "float"))
                vtype = self.typemap.get(hal_type, hal_type)
                virtual = signal_config.get("virtual")
                component = signal_config.get("component")
                if virtual and component:
                    # swap direction vor virt signals in component
                    if direction == "input":
                        direction = "output"
                    else:
                        direction = "input"
                elif virtual:
                    continue
                output.append(f'            "{varname}": {{')
                output.append(f'                "direction": "{direction}",')
                output.append(f'                "halname": "{halname}",')
                output.append(f'                "netname": "{netname}",')
                if not boolean:
                    output.append(f'                "type": "{vtype}",')
                    output.append('                "subs": {')
                    if not signal_source and not signal_config.get("helper", False):
                        if direction == "input" and hal_type == "float":
                            output.append(f'                    "{varname}_ABS": {{"type": "{vtype}"}},')
                            output.append(f'                    "{varname}_S32": {{"type": "int32"}},')
                            output.append(f'                    "{varname}_U32_ABS": {{"type": "uint32"}},')
                        if not virtual:
                            output.append(f'                    "{varname}_SCALE": {{"type": "float"}},')
                            output.append(f'                    "{varname}_OFFSET": {{"type": "float"}},')
                else:
                    output.append('                "type": "bool",')
                    output.append('                "subs": {')
                    if direction == "input":
                        output.append(f'                    "{varname}_not": {{"type": "bool"}},')
                    if signal_config.get("is_index_out"):
                        output.append(f'                    "{varname}_INDEX_RESET": {{"type": "bool"}},')
                        output.append(f'                    "{varname}_INDEX_WAIT": {{"type": "floatbool"}},')
                output.append("                },")
                output.append("            },")
        output.append("        }")
        output.append("")
        open(os.path.join(self.pylib_path, "rio.py"), "w").write("\n".join(output))

    def client_c(self):
        output = []
        output.append("")
        output.append("#include <unistd.h>")
        output.append("#include <stdint.h>")
        output.append("#include <stdlib.h>")
        output.append("#include <stdbool.h>")
        output.append("#include <stdio.h>")
        output.append("#include <string.h>")
        output.append("")
        output.append("#include <rio.h>")
        output.append("")
        output.append("data_t *data;")
        output.append("")
        output.append("int set_values(void) {")
        for plugin_instance in self.project.plugin_instances:
            if plugin_instance.master != self.instance.instances_name and plugin_instance.gmaster != self.instance.instances_name:
                continue
            for signal_name, signal_config in plugin_instance.signals().items():
                # halname = signal_config["halname"]
                varname = signal_config["varname"]
                direction = signal_config["direction"]
                boolean = signal_config.get("bool")
                virtual = signal_config.get("virtual")
                if virtual:
                    continue
                if direction == "output":
                    if boolean:
                        output.append(f"    *data->{varname} = 0;")
                    else:
                        output.append(f"    *data->{varname} = 0.0;")
        output.append("}")
        output.append("")

        output.append("int print_values(void) {")
        for plugin_instance in self.project.plugin_instances:
            if plugin_instance.master != self.instance.instances_name and plugin_instance.gmaster != self.instance.instances_name:
                continue
            for signal_name, signal_config in plugin_instance.signals().items():
                # halname = signal_config["halname"]
                varname = signal_config["varname"]
                direction = signal_config["direction"]
                boolean = signal_config.get("bool")
                virtual = signal_config.get("virtual")
                if virtual:
                    continue
                if direction == "input":
                    if boolean:
                        output.append(f'    printf("{varname}: %i\\n", *data->{varname});')
                    else:
                        output.append(f'    printf("{varname}: %f\\n", *data->{varname});')
        output.append('    printf("\\n");')
        output.append("}")
        output.append("")
        output.append("int main(int argc, char **argv) {")
        output.append("    data = init(argc, argv);")
        output.append("")
        output.append("    while (1) {")
        output.append("        set_values();")
        output.append("        rio_readwrite(NULL, 0);")
        output.append("        print_values();")
        output.append("")
        output.append("        usleep(100000);")
        output.append("    }")
        output.append("")
        output.append("    return 0;")
        output.append("}")
        output.append("")
        open(os.path.join(self.pylib_path, "rioclient.c"), "w").write("\n".join(output))

    def client_py(self):
        output = ["#!/usr/bin/python3"]
        output.append("#")
        output.append("#")
        output.append("")
        output.append("import sys")
        output.append("import time")
        output.append("from rio import RioWrapper")
        output.append("")

        output.append("def set_values(rio):")
        for plugin_instance in self.project.plugin_instances:
            if plugin_instance.master != self.instance.instances_name and plugin_instance.gmaster != self.instance.instances_name:
                continue
            for signal_name, signal_config in plugin_instance.signals().items():
                varname = signal_config["varname"]
                direction = signal_config["direction"]
                boolean = signal_config.get("bool")
                virtual = signal_config.get("virtual")
                if virtual:
                    continue
                if direction == "output":
                    if boolean:
                        output.append(f'    rio.data_set("{varname}", 0)')
                    else:
                        output.append(f'    rio.data_set("{varname}", 0.0)')
        output.append("")
        output.append("def print_values(rio):")
        output.append("    for name, config in rio.data_info().items():")
        output.append('        if config["direction"] == "input":')
        output.append("            print(f'{config[\"halname\"]} = {rio.data_get(name)}')")
        output.append('    print("")')
        output.append("")
        output.append("rio = RioWrapper()")
        output.append("")
        output.append("while True:")
        output.append("    set_values(rio)")
        output.append("    rio.rio_readwrite()")
        output.append("    print_values(rio)")
        output.append("    time.sleep(0.1)")
        output.append("")
        open(os.path.join(self.pylib_path, "rioclient.py"), "w").write("\n".join(output))

    def pylib_startscript(self):
        output = ["#!/bin/sh"]
        output.append("")
        output.append("set -e")
        output.append("set -x")
        output.append("")
        output.append('DIRNAME=`dirname "$0"`')
        output.append("")
        output.append('echo "compile package:"')
        output.append('(cd "$DIRNAME" && make clean all)')
        output.append("")
        output.append('echo "running rioclient:"')
        output.append("# LD_LIBRARY_PATH=$DIRNAME $DIRNAME/rioclient $@")
        output.append('cd "$DIRNAME" && python3 rioclient.py $@')
        output.append("")
        output.append("")
        os.makedirs(self.pylib_path, exist_ok=True)
        target = os.path.join(self.pylib_path, "start.sh")
        open(target, "w").write("\n".join(output))
        os.chmod(target, stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR | stat.S_IRGRP | stat.S_IXGRP | stat.S_IROTH | stat.S_IXOTH)

    def pylibname(self, halname):
        pylibname = halname.replace(".", "/").replace("-", "_")
        return f"{self.prefix}/{pylibname}"

    def vinit(self, vname, vtype, halstr=None, vdir="input"):
        vtype = self.typemap.get(vtype, vtype)
        return f"    data->{vname} = ({vtype}*)malloc(sizeof({vtype}));"
