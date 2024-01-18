import glob
import importlib
import os

riocore_path = os.path.dirname(os.path.dirname(__file__))

class Gateware:
    def __init__(self, project):
        self.project = project
        self.gateware_path = f"{project.config['output_path']}/Gateware"
        os.system(f"mkdir -p {self.gateware_path}/")

    def generator(self):
        self.verilogs = []
        self.top()
        self.makefile()

    def makefile(self):
        self.verilogs = []
        for plugin_instance in self.project.plugin_instances:
            for verilog in plugin_instance.gateware_files():
                if verilog in self.verilogs:
                    continue
                self.verilogs.append(verilog)
                ipv_path = f"{riocore_path}/plugins/{plugin_instance.NAME}/{verilog}"
                os.system(f"cp -a {ipv_path} {self.gateware_path}/{verilog}")

        for extrafile in ("debouncer.v", "toggle.v"):
            self.verilogs.append(extrafile)
            os.system(f"cp -a {riocore_path}/files/{extrafile} {self.gateware_path}/{extrafile}")
        self.verilogs.append("rio.v")
        self.config = self.project.config.copy()
        self.config["verilog_files"] = self.verilogs
        self.config["pinlists"] = {}
        self.config["pinlists"]["base"] = {}
        self.config["pinlists"]["base"]["sysclk_in"] = {"direction": "input", "pullup": False, "pin": self.config["sysclk_pin"], "varname": "sysclk_in"}
        # if self.config.get("error_pin"):
        #    self.config["pinlists"]["base"]["errorout"] = {"direction": "input", "pullup": True, "pin": self.config["error_pin"], "varname": "ERROR_OUT"}

        self.pinmapping = {}
        self.pinmapping_rev = {}
        for slot in self.config["board_data"].get("slots", []):
            slot_name = slot.get("name")
            slot_pins = slot.get("pins", {})
            for pin_name, pin in slot_pins.items():
                pin_id = f"{slot_name}:{pin_name}"
                self.pinmapping[pin_id] = pin
                self.pinmapping_rev[pin] = pin_id

        for plugin_instance in self.project.plugin_instances:
            self.config["pinlists"][plugin_instance.instances_name] = {}
            for pin_name, pin_config in plugin_instance.pins().items():
                if "pin" in pin_config and not pin_config["pin"].startswith("EXPANSION"):

                    pin_config["pin"] = self.pinmapping.get(pin_config["pin"], pin_config["pin"])

                    self.config["pinlists"][plugin_instance.instances_name][pin_name] = pin_config

        toolchain = self.config["toolchain"]
        print(f"loading toolchain {toolchain}")
        toolchain_generator = importlib.import_module(f".toolchain", f"riocore.generator.toolchains.{toolchain}")
        toolchain_generator.Toolchain(self.config).generate(self.gateware_path)

    def top(self):
        output = []
        input_variables_list = ["header_tx[7:0], header_tx[15:8], header_tx[23:16], header_tx[31:24]"]
        output_variables_list = []
        output_pos = self.project.buffer_size

        variable_name = "header_rx"
        size = 32
        pack_list = []
        for bit_num in range(0, size, 8):
            pack_list.append(f"rx_data[{output_pos-1}:{output_pos-8}]")
            output_pos -= 8
        output_variables_list.append(f"// assign {variable_name} = {{{', '.join(reversed(pack_list))}}};")

        if self.project.multiplexed_input:
            variable_name = "MULTIPLEXED_INPUT_VALUE"
            size = self.project.multiplexed_input_size
            pack_list = []
            for bit_num in range(0, size, 8):
                pack_list.append(f"{variable_name}[{bit_num+7}:{bit_num}]")
            input_variables_list.append(f"{', '.join(pack_list)}")
            variable_name = "MULTIPLEXED_INPUT_ID"
            size = 8
            pack_list = []
            for bit_num in range(0, size, 8):
                pack_list.append(f"{variable_name}[{bit_num+7}:{bit_num}]")
            input_variables_list.append(f"{', '.join(pack_list)}")

        if self.project.multiplexed_output:
            variable_name = "MULTIPLEXED_OUTPUT_VALUE"
            size = self.project.multiplexed_output_size
            pack_list = []
            for bit_num in range(0, size, 8):
                pack_list.append(f"rx_data[{output_pos-1}:{output_pos-8}]")
                output_pos -= 8
            output_variables_list.append(f"assign {variable_name} = {{{', '.join(reversed(pack_list))}}};")
            variable_name = "MULTIPLEXED_OUTPUT_ID"
            size = 8
            pack_list = []
            for bit_num in range(0, size, 8):
                pack_list.append(f"rx_data[{output_pos-1}:{output_pos-8}]")
                output_pos -= 8
            output_variables_list.append(f"assign {variable_name} = {{{', '.join(reversed(pack_list))}}};")

        for (size, plugin_instance, data_name, data_config) in self.project.get_interface_data():
            multiplexed = data_config.get("multiplexed", False)
            if multiplexed:
                continue
            variable_name = data_config["variable"]
            if data_config["direction"] == "input":
                pack_list = []
                if size >= 8:
                    for bit_num in range(0, size, 8):
                        pack_list.append(f"{variable_name}[{bit_num+7}:{bit_num}]")
                else:
                    pack_list.append(f"{variable_name}")
                input_variables_list.append(f"{', '.join(pack_list)}")
            elif data_config["direction"] == "output":
                pack_list = []
                if size >= 8:
                    for bit_num in range(0, size, 8):
                        pack_list.append(f"rx_data[{output_pos-1}:{output_pos-8}]")
                        output_pos -= 8
                else:
                    pack_list.append(f"rx_data[{output_pos-1}]")
                    output_pos -= 1
                output_variables_list.append(f"assign {variable_name} = {{{', '.join(reversed(pack_list))}}};")

        if self.project.buffer_size > self.project.input_size:
            diff = self.project.buffer_size - self.project.input_size
            input_variables_list.append(f"{diff}'d0")

        if self.project.buffer_size > self.project.output_size:
            diff = self.project.buffer_size - self.project.output_size
            output_variables_list.append(f"// assign FILL = rx_data[{diff-1}:0];")

        arguments_list = ["input sysclk_in"]
        for plugin_instance in self.project.plugin_instances:
            for pin_name, pin_config in plugin_instance.pins().items():
                if "pin" in pin_config and not pin_config["pin"].startswith("EXPANSION"):
                    arguments_list.append(f"{pin_config['direction'].lower()} {pin_config['varname']}")

        # arguments_list.append(f"output ERROR_OUT")

        output_name = ""
        output.append("/*")
        output.append(f"    ######### {self.project.config['name']} #########")
        output.append("")
        for key in ("toolchain", "family", "type", "package"):
            value = self.project.config[key]
            output.append(f"    {key.title():10}: {value}")
        output.append(f"    Clock     : {(self.project.config['speed'] / 1000000)} Mhz")
        output.append("")
        output.append("*/")
        output.append("")
        output.append("/* verilator lint_off UNUSEDSIGNAL */")
        output.append("")
        output.append("module rio (")
        arguments_string = ",\n        ".join(arguments_list)
        output.append(f"        {arguments_string}")
        output.append("    );")
        output.append("")
        output.append(f"    parameter BUFFER_SIZE = 16'd{self.project.buffer_size}; // {self.project.buffer_size//8} bytes")
        output.append("")
        output.append("    reg ESTOP = 0;")
        output.append("    wire ERROR;")
        output.append("    wire INTERFACE_TIMEOUT;")
        output.append("    wire INTERFACE_SYNC;")
        output.append("    assign ERROR = (INTERFACE_TIMEOUT | ESTOP);")
        # output.append("    assign ERROR_OUT = ERROR;")
        output.append("")

        osc_clock = self.project.config["osc_clock"]
        if osc_clock:
            speed = self.project.config["speed"]
            if self.project.config["jdata"]["family"] == "ecp5":
                os.system(f"ecppll -f '{self.gateware_path}/pll.v' -i {float(osc_clock) / 1000000} -o {float(speed) / 1000000}")
            elif self.project.config["jdata"]["type"] == "up5k":
                os.system(f"icepll -p -m -f '{self.gateware_path}/pll.v' -i {float(osc_clock) / 1000000} -o {float(speed) / 1000000}")
            elif self.project.config["jdata"]["family"] == "GW1N-9C":
                os.system(f"python3 {riocore_path}/files/gowin-pll.py -d 'GW1NR-9 C6/I5' -f '{self.gateware_path}/pll.v' -i {float(osc_clock) / 1000000} -o {float(speed) / 1000000}")
            elif self.project.config["jdata"]["family"] == "MAX 10":
                os.system(f"{riocore_path}/files/quartus-pll.sh \"{self.project.config['jdata']['family']}\" {float(osc_clock) / 1000000} {float(speed) / 1000000} '{self.gateware_path}/pll.v'")
            else:
                os.system(f"icepll -q -m -f '{self.gateware_path}/pll.v' -i {float(osc_clock) / 1000000} -o {float(speed) / 1000000}")
            self.verilogs.append("pll.v")
            output.append("    wire sysclk;")
            output.append("    wire locked;")
            if self.project.config["jdata"]["family"] == "MAX 10":
                output.append("    pll mypll(.inclk0(sysclk_in), .c0(sysclk), .locked(locked));")
            else:
                output.append("    pll mypll(sysclk_in, sysclk, locked);")
        else:
            output.append("    wire sysclk;")
            output.append("    assign sysclk = sysclk_in;")
        output.append("")

        output.append(f"    wire[{self.project.buffer_size-1}:0] rx_data;")
        output.append(f"    wire[{self.project.buffer_size-1}:0] tx_data;")
        output.append("")
        output.append("    reg signed [31:0] header_tx;")
        output.append("    always @(posedge sysclk) begin")
        output.append("        if (ESTOP) begin")
        output.append("            header_tx <= 32'h65737470;")
        output.append("        end else begin")
        output.append("            header_tx <= 32'h64617461;")
        output.append("        end")
        output.append("    end")
        output.append("")

        if self.project.multiplexed_input:
            output.append(f"    reg [{self.project.multiplexed_input_size-1}:0] MULTIPLEXED_INPUT_VALUE;")
            output.append("    reg [7:0] MULTIPLEXED_INPUT_ID;")
        if self.project.multiplexed_output:
            output.append(f"    wire [{self.project.multiplexed_output_size-1}:0] MULTIPLEXED_OUTPUT_VALUE;")
            output.append("    wire [7:0] MULTIPLEXED_OUTPUT_ID;")

        for plugin_instance in self.project.plugin_instances:
            for data_name, data_config in plugin_instance.interface_data().items():
                variable_name = data_config["variable"]
                variable_size = data_config["size"]
                direction = data_config["direction"]
                multiplexed = data_config.get("multiplexed", False)
                if variable_size > 1:
                    if multiplexed and direction == "output":
                        output.append(f"    reg [{variable_size-1}:0] {variable_name} = 0;")
                    else:
                        output.append(f"    wire [{variable_size-1}:0] {variable_name};")
                else:
                    output.append(f"    wire {variable_name};")
        output.append("")

        output_variables_string = "\n    ".join(output_variables_list)
        output.append(f"    {output_variables_string}")
        output.append("")

        output.append("    assign tx_data = {")
        input_variables_string = ",\n        ".join(input_variables_list)
        output.append(f"        {input_variables_string}")
        output.append("    };")
        output.append("")
        # gateware_defines
        for plugin_instance in self.project.plugin_instances:
            define_string = "\n    ".join(plugin_instance.gateware_defines())
            if define_string:
                output.append(f"    {define_string}")
        output.append("")

        # expansion assignments
        for plugin_instance in self.project.plugin_instances:
            for pin_name, pin_config in plugin_instance.pins().items():
                if "pin" in pin_config:
                    if pin_config["pin"].startswith("EXPANSION"):
                        output.append(f"    wire {pin_config['varname']};")
                        if pin_config["direction"] == "input":
                            output.append(f"    assign {pin_config['varname']} = {pin_config['pin']};")
                        elif pin_config["direction"] == "output":
                            output.append(f"    assign {pin_config['pin']} = {pin_config['varname']};")

        if self.project.multiplexed_input:
            output.append("    always @(posedge sysclk) begin")
            output.append(f"        if (INTERFACE_SYNC == 1) begin")
            output.append(f"            if (MULTIPLEXED_INPUT_ID < {self.project.multiplexed_input-1}) begin")
            output.append("                MULTIPLEXED_INPUT_ID = MULTIPLEXED_INPUT_ID + 1;")
            output.append("            end else begin")
            output.append(f"                MULTIPLEXED_INPUT_ID = 0;")
            output.append("            end")
            mpid = 0
            for (size, plugin_instance, data_name, data_config) in self.project.get_interface_data():
                multiplexed = data_config.get("multiplexed", False)
                if not multiplexed:
                    continue
                variable_name = data_config["variable"]
                direction = data_config["direction"]
                if direction == "input":
                    output.append(f"            if (MULTIPLEXED_INPUT_ID == {mpid}) begin")
                    output.append(f"                MULTIPLEXED_INPUT_VALUE <= {variable_name};")
                    output.append(f"            end")
                    mpid += 1
            output.append("        end")
            output.append("    end")

        if self.project.multiplexed_output:
            output.append("    always @(posedge sysclk) begin")
            mpid = 0
            for (size, plugin_instance, data_name, data_config) in self.project.get_interface_data():
                multiplexed = data_config.get("multiplexed", False)
                if not multiplexed:
                    continue
                variable_name = data_config["variable"]
                direction = data_config["direction"]
                if direction == "output":
                    output.append(f"        if (MULTIPLEXED_OUTPUT_ID == {mpid}) begin;")
                    output.append(f"            {variable_name} <= MULTIPLEXED_OUTPUT_VALUE;")
                    output.append(f"        end;")
                    mpid += 1
            output.append("    end")

        # gateware instances
        for plugin_instance in self.project.plugin_instances:
            output.append("")
            output.append(f"    // Name: {plugin_instance.plugin_setup.get('name', plugin_instance.instances_name)} ({plugin_instance.NAME})")
            for instance_name, instance_config in plugin_instance.gateware_instances().items():
                instance_module = instance_config.get("module")
                instance_parameter = instance_config.get("parameter")
                instance_arguments = instance_config.get("arguments")
                instance_predefines = instance_config.get("predefines")
                instance_direct = instance_config.get("direct")
                if instance_predefines:
                    predefines = "\n    ".join(instance_predefines)
                    output.append(f"    {predefines}")
                if not instance_direct:
                    if instance_arguments:
                        if instance_parameter:
                            output.append(f"    {instance_module} #(")
                            parameters_list = []
                            for parameter_name, parameter_value in instance_parameter.items():
                                parameters_list.append(f".{parameter_name}({parameter_value})")
                            parameters_string = ",\n        ".join(parameters_list)
                            output.append(f"        {parameters_string}")
                            output.append(f"    ) {instance_name} (")
                        else:
                            output.append(f"    {instance_module} {instance_name} (")
                        arguments_list = []
                        for argument_name, argument_value in instance_arguments.items():
                            arguments_list.append(f".{argument_name}({argument_value})")
                        arguments_string = ",\n        ".join(arguments_list)
                        output.append(f"        {arguments_string}")
                        output.append("    );")
        output.append("")
        output.append("endmodule")
        output.append("")
        print(f"writing gateware to: {self.gateware_path}")
        open(f"{self.gateware_path}/rio.v", "w").write("\n".join(output))

