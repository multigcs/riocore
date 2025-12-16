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
        #        "Python.h",
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

        self.pylib_makefile()
        self.pylib_startscript()
        self.pylib_page()

        output = self.mainh()
        open(os.path.join(self.pylib_path, "rio.h"), "w").write("\n".join(output))

        output = self.mainc(libmode=True)
        open(os.path.join(self.pylib_path, "rio.c"), "w").write("\n".join(output))

        output = self.pylib_functions()
        open(os.path.join(self.pylib_path, "riomodule.c"), "w").write("\n".join(output))

        output = self.pylib_functions_py()
        open(os.path.join(self.pylib_path, "riomodule.py"), "w").write("\n".join(output))

    def pylib_makefile(self):
        output = []
        output.append("")
        output.append("all: riomodule")
        output.append("")
        output.append("librio.so: rio.c")
        output.append("	gcc -shared -fPIC -o librio.so rio.c -I.")
        output.append("")
        output.append("riomodule: riomodule.c librio.so")
        output.append("	gcc -o riomodule riomodule.c -I. -L. -lrio")
        output.append("")
        output.append("clean:")
        output.append("	rm -rf riomodule librio.so")
        output.append("")
        open(os.path.join(self.pylib_path, "Makefile"), "w").write("\n".join(output))

    def pylib_page(self):
        output = []
        output.append("<html>")
        output.append("  <head>")
        output.append("    <title>RIO PYLIB</title>")
        output.append("  </head>")
        output.append("  <style>")
        output.append("""
body {
    font-family: Arial, sans-serif;
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}
.container {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 10px;
    padding: 20px;
}

.item {
    background-color: #f4f4f4;
    padding: 20px;
    text-align: center;
    border: 1px solid #ccc;
}

.tooltip {
  position: relative;
  display: inline-block;
  border-bottom: 1px dotted black; /* If you want dots under the hoverable text */
}

/* Tooltip text */
.tooltip .tooltiptext {
  visibility: hidden;
  width: 120px;
  background-color: black;
  color: #fff;
  text-align: center;
  padding: 5px 0;
  border-radius: 6px;
 
  /* Position the tooltip text - see examples below! */
  position: absolute;
  z-index: 1;
}

/* Show the tooltip text when you mouse over the tooltip container */
.tooltip:hover .tooltiptext {
  visibility: visible;
}

""")

        output.append("  </style>")
        output.append("  <body>")

        output.append('    <div class="container">')

        for plugin_instance in self.project.plugin_instances:
            if plugin_instance.master != self.instance.instances_name and plugin_instance.gmaster != self.instance.instances_name:
                continue
            signals = plugin_instance.signals()
            if not signals:
                continue
            output.append('        <div class="item">')
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
        output.append('    <script type="text/javascript">')
        output.append('        var clientID = "ID-" + Math.round(Math.random() * 1000);')
        output.append('        var client = new Paho.PYLIB.Client("127.0.0.1", 9001, clientID);')
        output.append("")

        for plugin_instance in self.project.plugin_instances:
            if plugin_instance.master != self.instance.instances_name and plugin_instance.gmaster != self.instance.instances_name:
                continue
            signals = plugin_instance.signals()
            if not signals:
                continue
            for signal_name, signal_config in signals.items():
                halname = signal_config["halname"]
                direction = signal_config["direction"]
                boolean = signal_config.get("bool")
                virtual = signal_config.get("virtual")
                if virtual:
                    continue
                if direction == "output":
                    vmin = signal_config.get("min", 0)
                    vmax = signal_config.get("max", 1000)
                    output.append(f'        document.getElementById("{self.pylibname(halname)}").addEventListener("change", publish, false);')
                    output.append(f'        document.getElementById("{self.pylibname(halname)}").addEventListener("input", publish, false);')
                    if vmin < 0:
                        output.append(f'        document.getElementById("{self.pylibname(halname)}_zero").addEventListener("click", publish, false);')

        output.append("        client.connect({onSuccess:onConnect});")
        output.append("        client.onMessageArrived = onMessage;")
        output.append("")
        output.append("        function onConnect() {")
        output.append('            console.log("connected");')

        for plugin_instance in self.project.plugin_instances:
            if plugin_instance.master != self.instance.instances_name and plugin_instance.gmaster != self.instance.instances_name:
                continue
            signals = plugin_instance.signals()
            if not signals:
                continue
            for signal_name, signal_config in signals.items():
                halname = signal_config["halname"]
                direction = signal_config["direction"]
                boolean = signal_config.get("bool")
                virtual = signal_config.get("virtual")
                if virtual:
                    continue
                if direction == "input":
                    output.append(f'            client.subscribe("{self.pylibname(halname)}");')

        output.append('            console.log("connected");')
        output.append("        }")
        output.append("")
        output.append("""
        function publish() {
            var topic = this.attributes.id.value.replace("_zero", "");
            element = document.getElementById(topic);
            var value = "0";
            if (element.attributes.type.value == "checkbox") {
                if (element.checked) {
                    value = "1";
                }
            } else {
                value = element.value;
            }
            console.log("publish", topic, value);

            fb_element = document.getElementById(topic + "_fb");
            if (fb_element) {
                fb_element.innerHTML = value;
            }


            var message = new Paho.PYLIB.Message(value);
            message.destinationName = topic;
            client.send(message);
        }
""")
        output.append("        function onMessage(message) {")
        output.append('            // console.log("msg", message.destinationName, message.payloadString);')

        for plugin_instance in self.project.plugin_instances:
            if plugin_instance.master != self.instance.instances_name and plugin_instance.gmaster != self.instance.instances_name:
                continue
            signals = plugin_instance.signals()
            if not signals:
                continue
            for signal_name, signal_config in signals.items():
                halname = signal_config["halname"]
                direction = signal_config["direction"]
                boolean = signal_config.get("bool")
                virtual = signal_config.get("virtual")
                if virtual:
                    continue
                if direction == "input":
                    output.append(f'            if (message.destinationName == "{self.pylibname(halname)}") {{')
                    output.append(f'                document.getElementById("{self.pylibname(halname)}").innerHTML = message.payloadString;')
                    output.append("            }")

        output.append("        }")
        output.append("")
        output.append("    </script>")
        output.append("  </body>")
        output.append("</html>")
        output.append("")
        open(os.path.join(self.pylib_path, "test.html"), "w").write("\n".join(output))

    def pylib_functions(self):
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
        return output

    def pylib_functions_py(self):
        output = ["#!/usr/bin/python3"]
        output.append("#")
        output.append("#")
        output.append("")
        output.append("import sys")
        output.append("import time")
        output.append("import ctypes")
        output.append("import pathlib")
        output.append("")
        output.append("def load_rio():")
        output.append('    libname = pathlib.Path().absolute() / "librio.so"')
        output.append("    rio = ctypes.CDLL(libname)")
        for plugin_instance in self.project.plugin_instances:
            if plugin_instance.master != self.instance.instances_name and plugin_instance.gmaster != self.instance.instances_name:
                continue
            for signal_name, signal_config in plugin_instance.signals().items():
                halname = signal_config["halname"].replace(".", "_")
                # varname = signal_config["varname"]
                direction = signal_config["direction"]
                boolean = signal_config.get("bool")
                virtual = signal_config.get("virtual")
                if virtual:
                    continue
                if direction == "input":
                    if boolean:
                        output.append(f"    rio.get_{halname}.restype = ctypes.c_bool")
                    else:
                        output.append(f"    rio.get_{halname}.restype = ctypes.c_float")
                elif direction == "output":
                    if boolean:
                        output.append(f"    rio.set_{halname}.argtypes = [ctypes.c_bool]")
                    else:
                        output.append(f"    rio.set_{halname}.argtypes = [ctypes.c_float]")
        output.append("")
        output.append("    p_args = list((arg.encode() for arg in sys.argv))")
        output.append("    args = (ctypes.c_char_p * len(p_args))(*p_args)")
        output.append("    rio.init(len(args), args)")
        output.append("")
        output.append("    return rio")
        output.append("")

        output.append("def set_values():")
        for plugin_instance in self.project.plugin_instances:
            if plugin_instance.master != self.instance.instances_name and plugin_instance.gmaster != self.instance.instances_name:
                continue
            for signal_name, signal_config in plugin_instance.signals().items():
                halname = signal_config["halname"].replace(".", "_")
                # varname = signal_config["varname"]
                direction = signal_config["direction"]
                boolean = signal_config.get("bool")
                virtual = signal_config.get("virtual")
                if virtual:
                    continue
                if direction == "output":
                    if boolean:
                        output.append(f"    rio.set_{halname}(0)")
                    else:
                        output.append(f"    rio.set_{halname}(0.0)")
        output.append("")

        output.append("def print_values():")
        for plugin_instance in self.project.plugin_instances:
            if plugin_instance.master != self.instance.instances_name and plugin_instance.gmaster != self.instance.instances_name:
                continue
            for signal_name, signal_config in plugin_instance.signals().items():
                halname = signal_config["halname"].replace(".", "_")
                # varname = signal_config["varname"]
                direction = signal_config["direction"]
                boolean = signal_config.get("bool")
                virtual = signal_config.get("virtual")
                if virtual:
                    continue
                if direction == "input":
                    output.append(f"    value = rio.get_{halname}()")
                    output.append(f'    print("{halname}", value)')
        output.append('    print("")')
        output.append("")

        output.append("rio = load_rio()")
        output.append("")
        output.append("while True:")
        output.append("")
        output.append("    set_values()")
        output.append("    rio.rio_readwrite(None, 0)")
        output.append("    print_values()")
        output.append("")
        output.append("    time.sleep(0.1)")
        output.append("")

        return output

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
        output.append('echo "running riomodule:"')
        output.append("# LD_LIBRARY_PATH=$DIRNAME $DIRNAME/riomodule $@")
        output.append('cd "$DIRNAME" && python3 riomodule.py $@')
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
