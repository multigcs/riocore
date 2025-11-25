import json
import os

import riocore
from riocore import Plugins
from riocore.plugins import PluginBase

riocore_path = os.path.dirname(riocore.__file__)


class Plugin(PluginBase):
    def setup(self):
        self.NAME = "riosub"
        self.INFO = "rio sub board"
        self.DESCRIPTION = """to combine multible RIO boards via RS422 and/or RS485

* the sub config must setup 'uart' as interface with checksum activated

        """
        self.GRAPH = """
graph LR;
    Host<--udp/spi-->FPGA1;
    FPGA1-->plugin1;
    FPGA1-->plugin2;
    FPGA1<--RS422-->FPGA2;
    FPGA2-->plugin3;
    FPGA2-->plugin4;
        """
        self.KEYWORDS = ""
        self.ORIGIN = ""
        self.EXPERIMENTAL = True
        self.VERILOGS = ["uart_baud.v", "uart_rx.v", "uart_tx.v"]
        self.PINDEFAULTS = {}
        self.PINDEFAULTS = {
            "tx": {
                "direction": "output",
            },
            "rx": {
                "direction": "input",
            },
            "tx_enable": {
                "direction": "output",
                "optional": True,
                "descruption": "for RS485 mode",
            },
        }
        self.INTERFACE = {
            "valid": {
                "size": 1,
                "direction": "input",
            },
        }
        self.SIGNALS = {
            "valid": {
                "direction": "input",
                "bool": True,
            },
        }
        self.OPTIONS = {
            "subconfig": {
                "default": "",
                "type": "file",
                "unit": "",
                "description": "sub json-config file",
            },
            "baud": {
                "default": 1000000,
                "type": int,
                "min": 9600,
                "max": 10000000,
                "unit": "bit/s",
                "description": "serial baud rate",
            },
        }
        self.plugins = Plugins()
        self.plugin_modules = {}
        self.sub_plugins_id = 100
        self.sub_plugins = {}
        self.sub_signals = {}

        self.buffersize_tx = 32  # Header
        self.buffersize_rx = 32 + 32  # Header + timestamp

        subconfig = self.plugin_setup.get("subconfig", self.OPTIONS["subconfig"]["default"])
        if not subconfig:
            return

        if not os.path.isfile(subconfig):
            print(f"ERROR: can not load sub config: {subconfig}")
            return

        if subconfig:
            subdata_json = open(subconfig).read()
            subdata = json.loads(subdata_json)
            for sub_plugin in subdata["plugins"]:
                sub_plugin["instance"] = self.plugins.load_plugin(self.sub_plugins_id, sub_plugin, system_setup=self.system_setup, subfix=f"{self.instances_name}_")
                sub_plugin["name"] = f"{sub_plugin['type']}{self.sub_plugins_id}"
                self.sub_plugins[sub_plugin["name"]] = sub_plugin
                self.sub_plugins_id += 1

            for sub_plugin in subdata["plugins"]:
                for signal_name, signal_defaults in sub_plugin["instance"].SIGNALS.items():
                    self.SIGNALS[f"{sub_plugin['name']}_{signal_name}"] = signal_defaults
                    self.sub_signals[f"{sub_plugin['name']}_{signal_name}"] = (sub_plugin, signal_name)

                for interface_name, interface_defaults in sub_plugin["instance"].INTERFACE.items():
                    self.INTERFACE[f"{sub_plugin['name']}_{interface_name}"] = interface_defaults

            # checking multiplexed values
            self.multiplexed_input = 0
            self.multiplexed_output = 0
            self.multiplexed_input_size = 0
            self.multiplexed_output_size = 0
            for sub_plugin in subdata["plugins"]:
                for interface_name, interface_defaults in sub_plugin["instance"].INTERFACE.items():
                    multiplexed = interface_defaults.get("multiplexed", False)
                    if not multiplexed:
                        continue
                    size = interface_defaults["size"]
                    direction = interface_defaults["direction"]
                    if size == 1:
                        size = 8
                    if direction == "input":
                        self.multiplexed_input += 1
                        self.multiplexed_input_size = max(self.multiplexed_input_size, size)
                    else:
                        self.multiplexed_output += 1
                        self.multiplexed_output_size = max(self.multiplexed_output_size, size)

            if self.multiplexed_output:
                self.buffersize_tx += self.multiplexed_output_size + 8
            if self.multiplexed_input:
                self.buffersize_rx += self.multiplexed_input_size + 8

            # check frame size
            for sub_plugin in subdata["plugins"]:
                for interface_name, interface_defaults in sub_plugin["instance"].INTERFACE.items():
                    multiplexed = interface_defaults.get("multiplexed", False)
                    size = interface_defaults["size"]
                    direction = interface_defaults["direction"]
                    if multiplexed:
                        continue

                    if direction == "output":
                        self.buffersize_tx += size
                    else:
                        self.buffersize_rx += size

            self.buffersize = max(self.buffersize_tx, self.buffersize_rx)
            self.buffersize_bytes = (self.buffersize + 7) // 8
            self.buffersize = self.buffersize_bytes * 8
            self.tx_fill = max(0, self.buffersize_bytes * 8 - self.buffersize_tx)
            self.rx_fill = max(0, self.buffersize_bytes * 8 - self.buffersize_rx)

            # csum
            self.buffersize_bytes += 2

            input_pos = self.buffersize
            self.tx_frame = ["32'h74697277"]
            self.rx_frame = []

            input_pos -= 32
            self.rx_frame.append(f"// HEADER / input_pos={input_pos} -> {input_pos + 32}")
            input_pos -= 32
            self.rx_frame.append(f"// TIMESTAMP / input_pos={input_pos} -> {input_pos + 32}")

            # csum
            input_pos += 16

            # building rx/tx frames
            if self.multiplexed_input:
                variable_name = "MULTIPLEXED_INPUT_VALUE"
                size = self.multiplexed_input_size
                pack_list = []
                for bit_num in range(0, size, 8):
                    pack_list.append(f"rx_frame[{input_pos - 1}:{input_pos - 8}]")
                    input_pos -= 8
                self.rx_frame.append(f"assign {variable_name} = {{{', '.join(reversed(pack_list))}}}; // input_pos={input_pos}")
                variable_name = "MULTIPLEXED_INPUT_ID"
                size = 8
                pack_list = []
                for bit_num in range(0, size, 8):
                    pack_list.append(f"rx_frame[{input_pos - 1}:{input_pos - 8}]")
                    input_pos -= 8
                self.rx_frame.append(f"assign {variable_name} = {{{', '.join(reversed(pack_list))}}}; // input_pos={input_pos}")

            if self.multiplexed_output:
                variable_name = "MULTIPLEXED_OUTPUT_VALUE"
                size = self.multiplexed_output_size
                pack_list = []
                for bit_num in range(0, size, 8):
                    pack_list.append(f"{variable_name}[{bit_num + 7}:{bit_num}]")
                self.tx_frame.append(", ".join(pack_list))
                variable_name = "MULTIPLEXED_OUTPUT_ID"
                size = 8
                pack_list = []
                for bit_num in range(0, size, 8):
                    pack_list.append(f"{variable_name}[{bit_num + 7}:{bit_num}]")
                self.tx_frame.append(", ".join(pack_list))

            for check_size in range(128, 0, -1):
                for sub_plugin in subdata["plugins"]:
                    for interface_name, interface_defaults in sub_plugin["instance"].INTERFACE.items():
                        multiplexed = interface_defaults.get("multiplexed", False)
                        if multiplexed:
                            continue
                        size = interface_defaults["size"]
                        if check_size != size:
                            continue
                        direction = interface_defaults["direction"]
                        variable_name = f"{sub_plugin['name']}_{interface_name}"
                        if direction == "output":
                            pack_list = []
                            if size >= 8:
                                for bit_num in range(0, size, 8):
                                    pack_list.append(f"{variable_name}[{bit_num + 7}:{bit_num}]")
                            else:
                                pack_list.append(f"{variable_name}")
                            self.tx_frame.append(", ".join(pack_list))
                        else:
                            pack_list = []
                            if size >= 8:
                                for bit_num in range(0, size, 8):
                                    pack_list.append(f"rx_frame[{input_pos - 1}:{input_pos - 8}]")
                                    input_pos -= 8
                            elif size > 1:
                                pack_list.append(f"rx_frame[{input_pos - 1}:{input_pos - size}]")
                                input_pos -= size
                            else:
                                pack_list.append(f"rx_frame[{input_pos - 1}]")
                                input_pos -= 1
                            self.rx_frame.append(f"assign {variable_name} = {{{', '.join(reversed(pack_list))}}}; // input_pos={input_pos}")

            # RX
            input_pos -= self.rx_fill
            self.rx_frame.append(f"// {self.rx_fill}bit FILL / input_pos={input_pos}")
            input_pos -= 16
            self.rx_frame.append(f"// CSUM / input_pos={input_pos}")

        if self.tx_fill:
            self.tx_frame.append(f"{self.tx_fill}'d0, // FILL")

        self.tx_frame.append("16'd0 // CSUM")

        self.tx_frame_fmt = ",\n        ".join(self.tx_frame)

        verilog_data = []
        verilog_data.append("")
        verilog_data.append(f"module riosub_{self.instances_name}")
        verilog_data.append(f"    #(parameter BUFFER_SIZE={self.buffersize_bytes}, parameter ClkFrequency=12000000, parameter Baud=9600, parameter TX_DELAY=10000)")
        verilog_data.append("    (")
        verilog_data.append("        input clk,")

        for sub_plugin in subdata["plugins"]:
            for interface_name, interface_defaults in sub_plugin["instance"].INTERFACE.items():
                multiplexed = interface_defaults.get("multiplexed", False)
                size = interface_defaults["size"]
                direction = interface_defaults["direction"]
                varname = f"{sub_plugin['name']}_{interface_name}"
                if direction == "input":
                    rev_direction = "output"
                    if multiplexed:
                        if size > 1:
                            verilog_data.append(f"        {rev_direction} reg [{size - 1}:0] {varname} = 0,")
                        else:
                            verilog_data.append(f"        {rev_direction} reg {varname} = 0,")
                    elif size > 1:
                        verilog_data.append(f"        {rev_direction} [{size - 1}:0] {varname},")
                    else:
                        verilog_data.append(f"        {rev_direction} {varname},")
                else:
                    rev_direction = "input"
                    if size > 1:
                        verilog_data.append(f"        {rev_direction} [{size - 1}:0] {varname},")
                    else:
                        verilog_data.append(f"        {rev_direction} {varname},")

        verilog_data.append("        output reg tx_enable = 0,")
        verilog_data.append("        output reg valid = 0,")
        verilog_data.append("        input rx,")
        verilog_data.append("        output tx")
        verilog_data.append("    );")
        verilog_data.append("")
        verilog_data.append("    localparam BUFFER_SIZE_BITS = BUFFER_SIZE * 8;")
        verilog_data.append("")
        verilog_data.append("    reg [15:0] rx_csum = 0;")
        verilog_data.append("    reg [15:0] tx_csum = 0;")
        verilog_data.append("    reg [(BUFFER_SIZE_BITS)-1:0] rx_frame = 0;")
        verilog_data.append("    wire [(BUFFER_SIZE_BITS)-1:0] tx_frame;")
        verilog_data.append("    assign tx_frame = {")
        verilog_data.append(f"        {self.tx_frame_fmt}")
        verilog_data.append("    };")

        for part in self.rx_frame:
            verilog_data.append(f"    {part}")

        verilog_data.append("")
        verilog_data.append("    reg isync = 0;")
        verilog_data.append("    reg [7:0] state = 0;")
        verilog_data.append("    reg [31:0] delay_counter = 0;")
        verilog_data.append("    reg [31:0] rx_byte_counter = 0;")
        verilog_data.append("    reg [31:0] tx_byte_counter = 0;")
        verilog_data.append("    reg [(BUFFER_SIZE_BITS)-1:0] tx_data = 0;")
        verilog_data.append("    reg [(BUFFER_SIZE_BITS)-1:0] rx_data = 0;")
        verilog_data.append("")

        if self.multiplexed_input:
            verilog_data.append(f"    wire [{self.multiplexed_input_size - 1}:0] MULTIPLEXED_INPUT_VALUE;")
            verilog_data.append("    wire [7:0] MULTIPLEXED_INPUT_ID;")
            verilog_data.append("    always @(posedge clk) begin")
            mpid = 0
            for check_size in range(self.multiplexed_input_size, 0, -1):
                for sub_plugin in subdata["plugins"]:
                    for interface_name, interface_defaults in sub_plugin["instance"].INTERFACE.items():
                        multiplexed = interface_defaults.get("multiplexed", False)
                        if not multiplexed:
                            continue
                        size = interface_defaults["size"]
                        if size != check_size:
                            continue
                        variable_name = f"{sub_plugin['name']}_{interface_name}"
                        direction = interface_defaults["direction"]
                        if direction == "input":
                            verilog_data.append(f"        if (MULTIPLEXED_INPUT_ID == {mpid}) begin")
                            verilog_data.append(f"            {variable_name} <= MULTIPLEXED_INPUT_VALUE[{size - 1}:0];")
                            verilog_data.append("        end")
                            mpid += 1
            verilog_data.append("    end")

        if self.multiplexed_output:
            verilog_data.append(f"    reg [{self.multiplexed_output_size - 1}:0] MULTIPLEXED_OUTPUT_VALUE = 0;")
            verilog_data.append("    reg [7:0] MULTIPLEXED_OUTPUT_ID = 0;")
            verilog_data.append("    always @(posedge clk) begin")
            verilog_data.append("        if (isync == 1) begin")
            verilog_data.append(f"            if (MULTIPLEXED_OUTPUT_ID < {self.multiplexed_output - 1}) begin")
            verilog_data.append("                MULTIPLEXED_OUTPUT_ID = MULTIPLEXED_OUTPUT_ID + 1'd1;")
            verilog_data.append("            end else begin")
            verilog_data.append("                MULTIPLEXED_OUTPUT_ID = 0;")
            verilog_data.append("            end")
            mpid = 0
            # sort by size
            for check_size in range(self.multiplexed_output_size, 0, -1):
                for sub_plugin in subdata["plugins"]:
                    for interface_name, interface_defaults in sub_plugin["instance"].INTERFACE.items():
                        multiplexed = interface_defaults.get("multiplexed", False)
                        if not multiplexed:
                            continue
                        size = interface_defaults["size"]
                        if size != check_size:
                            continue
                        variable_name = f"{sub_plugin['name']}_{interface_name}"
                        direction = interface_defaults["direction"]
                        if direction == "output":
                            verilog_data.append(f"            if (MULTIPLEXED_OUTPUT_ID == {mpid}) begin")
                            if size == 1:
                                verilog_data.append(f"                MULTIPLEXED_OUTPUT_VALUE <= {variable_name};")
                            else:
                                verilog_data.append(f"                MULTIPLEXED_OUTPUT_VALUE <= {variable_name}[{size - 1}:0];")
                            verilog_data.append("            end")
                            mpid += 1

            verilog_data.append("        end")
            verilog_data.append("    end")

        verilog_data.append("""
    always @(posedge clk) begin
        TxD_start <= 0;
        isync <= 0;

        if (state == 0) begin
            tx_data <= tx_frame;
            tx_csum <= 0;
            state <= 1;

        end else if (state == 1) begin
            // tx next bytes
            if (TxD_busy == 0 && TxD_start == 0) begin
                TxD_data <= tx_data[(BUFFER_SIZE_BITS)-1:(BUFFER_SIZE_BITS)-8];
                if (tx_byte_counter < BUFFER_SIZE - 2) begin
                    tx_csum <= tx_csum + tx_data[(BUFFER_SIZE_BITS)-1:(BUFFER_SIZE_BITS)-8] + 1;
                end
                TxD_start <= 1;
                state <= 2;
            end
        end else if (state == 2) begin
            if (TxD_busy == 0) begin
                state <= 3;
            end
        end else if (state == 3) begin
            if (TxD_busy == 0) begin
                if (tx_byte_counter < BUFFER_SIZE - 1) begin
                    if (tx_byte_counter < BUFFER_SIZE - 1 - 2) begin
                        tx_data <= {tx_data[(BUFFER_SIZE_BITS)-8-1:0], 8'd0};
                    end else if (tx_byte_counter < BUFFER_SIZE - 1 - 1) begin
                        tx_data[(BUFFER_SIZE_BITS)-1:(BUFFER_SIZE_BITS)-8] <= tx_csum[15:8];
                    end else if (tx_byte_counter < BUFFER_SIZE - 1) begin
                        tx_data[(BUFFER_SIZE_BITS)-1:(BUFFER_SIZE_BITS)-8] <= tx_csum[7:0];
                    end

                    state <= 1;
                    tx_byte_counter <= tx_byte_counter + 1;
                end else begin
                    state <= 4;
                    tx_byte_counter <= 0;
                    tx_enable <= 0;
                end
            end

        end else if (state == 4) begin
            if (delay_counter < TX_DELAY) begin
                delay_counter <= delay_counter + 1;
            end else begin
                delay_counter <= 0;
                state <= 0;
                isync <= 1;
                tx_enable <= 1;
            end
        end

        if (RxD_endofpacket == 1) begin
            if (rx_data[BUFFER_SIZE_BITS-1:BUFFER_SIZE_BITS-32] == 32'h61746164 && rx_data[15:0] == rx_csum) begin
            //if (rx_data[BUFFER_SIZE_BITS-1:BUFFER_SIZE_BITS-32] == 32'h61746164) begin
                valid <= 1;
                rx_frame <= rx_data;
            end else begin
                valid <= 0;
            end
            rx_data <= 0;
            rx_byte_counter <= 0;
            rx_csum <= 0;
            delay_counter <= TX_DELAY;
        end else if (RxD_data_ready == 1) begin
            if (rx_byte_counter < BUFFER_SIZE) begin
                rx_data <= {rx_data[(BUFFER_SIZE_BITS)-8-1:0], RxD_data};
                if (rx_byte_counter < BUFFER_SIZE - 2) begin
                    rx_csum <= rx_csum + RxD_data + 1;
                end

                rx_byte_counter <= rx_byte_counter + 1;
            end
        end
    end

    reg TxD_start = 0;
    wire TxD_busy;
    reg [7:0] TxD_data = 0;
    uart_tx #(ClkFrequency, Baud) uart_tx1 (
        .clk (clk),
        .TxD (tx),
        .TxD_data (TxD_data),
        .TxD_start (TxD_start),
        .TxD_busy (TxD_busy)
    );

    wire [7:0] RxD_data;
    wire RxD_data_ready;
    wire RxD_idle;
    wire RxD_endofpacket;

    uart_rx #(ClkFrequency, Baud) uart_rx1 (
        .clk (clk),
        .RxD (rx),
        .RxD_data_ready (RxD_data_ready),
        .RxD_data (RxD_data),
        .RxD_idle (RxD_idle),
        .RxD_endofpacket (RxD_endofpacket)
    );

endmodule

""")

        self.VERILOGS_DATA = {f"riosub_{self.instances_name}.v": "\n".join(verilog_data)}

    def gateware_instances(self):
        instances = self.gateware_instances_base()
        instance = instances[self.instances_name]
        instance_parameter = instance["parameter"]
        instance["module"] = f"riosub_{self.instances_name}"
        instance_parameter["ClkFrequency"] = self.system_setup["speed"]
        baud = int(self.plugin_setup.get("baud", self.OPTIONS["baud"]["default"]))
        instance_parameter["Baud"] = baud
        instance_parameter["TX_DELAY"] = self.system_setup["speed"] // 1000
        return instances

    def convert(self, signal_name, signal_setup, value):
        if signal_name in {"valid"}:
            return value
        sub_plugin = self.sub_signals[signal_name][0]
        sub_signal_name = self.sub_signals[signal_name][1]
        instance = sub_plugin["instance"]
        signals = instance.signals()
        if sub_signal_name in signals:
            value = instance.convert(sub_signal_name, signals[sub_signal_name], value)
        return value

    def convert_c(self, signal_name, signal_setup):
        if signal_name in {"valid"}:
            return ""
        sub_plugin = self.sub_signals[signal_name][0]
        sub_signal_name = self.sub_signals[signal_name][1]
        instance = sub_plugin["instance"]
        signals = instance.signals()
        calc = ""
        if sub_signal_name in signals:
            for sig_conf in instance.SIGNALS.values():
                sig_conf["varname"] = sig_conf["varname"].replace("SIGIN_", f"SIGIN_{self.instances_name.upper()}_".replace("SIGOUT_", f"SIGOUT_{self.instances_name.upper()}_"))
            calc = instance.convert_c(sub_signal_name, signals[sub_signal_name])
        return calc
