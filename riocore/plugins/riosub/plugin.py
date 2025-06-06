import os
import json
import sys
import traceback
import importlib

import riocore
from riocore.plugins import PluginBase

riocore_path = os.path.dirname(riocore.__file__)


class Plugin(PluginBase):
    def setup(self):
        self.NAME = "riosub"
        self.INFO = "rio sub board"
        self.DESCRIPTION = """to combine multible RIO boards via RS422

* the sub config must setup 'uart' as interface
* very limited !!!
* very buggy !!!
* some calculations will not work
* some plugins will not work
* only for testing

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
        }
        self.INTERFACE = {}
        self.SIGNALS = {}
        self.OPTIONS = {
            "subconfig": {
                "default": "",
                "type": str,
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
        self.plugin_modules = {}
        self.plugin_instances = []
        self.sub_plugins_id = 0
        self.sub_plugins = {}
        self.sub_signals = {}

        self.buffersize_tx = 4 * 8  # Header
        self.buffersize_rx = 4 * 8 + 4 * 8  # Header + timestamp

        subconfig = self.plugin_setup.get("subconfig", self.OPTIONS["subconfig"]["default"])
        if not subconfig:
            return

        if subconfig:
            subdata_json = open(subconfig, "r").read()
            subdata = json.loads(subdata_json)

            for sub_plugin in subdata["plugins"]:
                sub_plugin["instance"] = self.load_plugin(sub_plugin["type"], sub_plugin, system_setup=self.system_setup)
                sub_plugin["name"] = f"{sub_plugin['type']}{self.sub_plugins_id}"
                self.sub_plugins[sub_plugin["name"]] = sub_plugin
                self.sub_plugins_id += 1

            for sub_plugin in subdata["plugins"]:
                for signal_name, signal_defaults in sub_plugin["instance"].SIGNALS.items():
                    self.SIGNALS[f"{sub_plugin['name']}_{signal_name}"] = signal_defaults
                    self.sub_signals[f"{sub_plugin['name']}_{signal_name}"] = (sub_plugin, signal_name)

                for interface_name, interface_defaults in sub_plugin["instance"].INTERFACE.items():
                    self.INTERFACE[f"{sub_plugin['name']}_{interface_name}"] = interface_defaults
                    size = interface_defaults["size"]
                    direction = interface_defaults["direction"]

                    if direction == "output":
                        self.buffersize_tx += size
                    else:
                        self.buffersize_rx += size

            output_pos = self.buffersize_rx - 32 - 32
            self.tx_frame = ["32'h74697277"]
            self.rx_frame = []

            for sub_plugin in subdata["plugins"]:
                for interface_name, interface_defaults in sub_plugin["instance"].INTERFACE.items():
                    size = interface_defaults["size"]
                    direction = interface_defaults["direction"]
                    variable_name = f"{sub_plugin['name']}_{interface_name}"
                    if direction == "output":
                        pack_list = []
                        if size >= 8:
                            for bit_num in range(0, size, 8):
                                # for bit_num in range(size - 8, -8, -8):
                                pack_list.append(f"{variable_name}[{bit_num + 7}:{bit_num}]")
                        else:
                            pack_list.append(f"{variable_name}")
                        self.tx_frame.append(", ".join(pack_list))
                    else:
                        pack_list = []
                        if size >= 8:
                            for bit_num in range(0, size, 8):
                                pack_list.append(f"rx_frame[{output_pos - 1}:{output_pos - 8}]")
                                output_pos -= 8
                        elif size > 1:
                            pack_list.append(f"rx_frame[{output_pos - 1}:{output_pos - size}]")
                            output_pos -= size
                        else:
                            pack_list.append(f"rx_frame[{output_pos - 1}]")
                            output_pos -= 1
                        self.rx_frame.append(f"assign {variable_name} = {{{', '.join(reversed(pack_list))}}};")

        self.buffersize = max(self.buffersize_tx, self.buffersize_rx)
        self.buffersize_bytes = (self.buffersize + 7) // 8
        self.tx_fill = self.buffersize_bytes * 8 - self.buffersize_tx

        if self.tx_fill:
            self.tx_frame.append(f"{self.tx_fill}'d0")
        self.tx_frame_fmt = ",\n        ".join(self.tx_frame)

        verilog_data = []
        verilog_data.append("")
        verilog_data.append(f"module riosub_{self.instances_name}")
        verilog_data.append(f"    #(parameter BUFFER_SIZE={self.buffersize_bytes}, parameter ClkFrequency=12000000, parameter Baud=9600)")
        verilog_data.append("    (")
        verilog_data.append("        input clk,")
        if subconfig:
            for sub_plugin in subdata["plugins"]:
                for interface_name, interface_defaults in sub_plugin["instance"].INTERFACE.items():
                    size = interface_defaults["size"]
                    direction = interface_defaults["direction"]
                    varname = f"{sub_plugin['name']}_{interface_name}"
                    if direction == "input":
                        rev_direction = "output"
                    else:
                        rev_direction = "input"
                    if size > 1:
                        verilog_data.append(f"        {rev_direction} [{size - 1}:0] {varname},")
                    else:
                        verilog_data.append(f"        {rev_direction} {varname},")

        verilog_data.append("        input rx,")
        verilog_data.append("        output tx")
        verilog_data.append("    );")
        verilog_data.append("")
        verilog_data.append("    reg [(BUFFER_SIZE*8)-1:0] rx_frame = 0;")
        verilog_data.append("    wire [(BUFFER_SIZE*8)-1:0] tx_frame;")
        verilog_data.append("    assign tx_frame = {")
        verilog_data.append(f"        {self.tx_frame_fmt}")
        verilog_data.append("    };")

        for part in self.rx_frame:
            verilog_data.append(f"    {part}")

        verilog_data.append("")
        verilog_data.append("    reg [7:0] state = 0;")
        verilog_data.append("    reg [31:0] counter = 0;")
        verilog_data.append("    reg [31:0] rx_byte_counter = 0;")
        verilog_data.append("    reg [31:0] tx_byte_counter = 0;")
        verilog_data.append("    reg [(BUFFER_SIZE*8)-1:0] tx_data = 0;")
        verilog_data.append("    reg [(BUFFER_SIZE*8)-1:0] rx_data = 0;")
        verilog_data.append("")
        verilog_data.append("""

    always @(posedge clk) begin
        TxD_start <= 0;

        if (state == 0) begin
            tx_data <= tx_frame;
            state <= 1;

        end else if (state == 1) begin
            // tx next bytes
            if (TxD_busy == 0 && TxD_start == 0) begin
                TxD_data <= tx_data[(BUFFER_SIZE*8)-1:(BUFFER_SIZE*8)-8];
                TxD_start <= 1;
                state <= 2;
                tx_data <= {tx_data[(BUFFER_SIZE*8)-8:0], 8'd0};
            end

        end else if (state == 2) begin
            if (TxD_busy == 0) begin
                if (tx_byte_counter < BUFFER_SIZE-1) begin
                    state <= 1;
                    tx_byte_counter <= tx_byte_counter + 1;
                end else begin
                    state <= 3;
                    tx_byte_counter <= 0;
                end
            end

        end else if (state == 3) begin
            if (counter < 1000) begin
                counter <= counter + 1;
            end else begin
                counter <= 0;
                state <= 0;
            end
        end

        if (RxD_endofpacket == 1) begin
            rx_frame <= rx_data;
            rx_data <= 0;
            rx_byte_counter <= 0;
        end else if (RxD_data_ready == 1) begin
            if (rx_byte_counter < BUFFER_SIZE) begin
                rx_data <= {rx_data[(BUFFER_SIZE*8)-8-1:0], RxD_data};
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
        return instances

    def convert(self, signal_name, signal_setup, value):
        sub_plugin = self.sub_signals[signal_name][0]
        sub_signal_name = self.sub_signals[signal_name][1]
        instance = sub_plugin["instance"]
        signals = instance.signals()
        if sub_signal_name in signals:
            value = instance.convert(sub_signal_name, signals[sub_signal_name], value)
        return value

    def convert_c(self, signal_name, signal_setup):
        sub_plugin = self.sub_signals[signal_name][0]
        sub_signal_name = self.sub_signals[signal_name][1]
        instance = sub_plugin["instance"]
        signals = instance.signals()
        calc = ""
        if sub_signal_name in signals:
            for sig, sig_conf in instance.SIGNALS.items():
                sig_conf["varname"] = sig_conf["varname"].replace("SIGIN_", f"SIGIN_{self.instances_name.upper()}_".replace("SIGOUT_", f"SIGOUT_{self.instances_name.upper()}_"))
            calc = instance.convert_c(sub_signal_name, signals[sub_signal_name])
        return calc

    def load_plugin(self, plugin_id, plugin_config, system_setup=None):
        try:
            plugin_type = plugin_config["type"]
            if plugin_type not in self.plugin_modules:
                if os.path.isfile(os.path.join(riocore_path, "plugins", plugin_type, "plugin.py")):
                    self.plugin_modules[plugin_type] = importlib.import_module(".plugin", f"riocore.plugins.{plugin_type}")
                elif not plugin_type or plugin_type[0] != "_":
                    print(f"WARNING: SUB: plugin not found: {plugin_type}", os.path.join(riocore_path, "plugins", plugin_type, "plugin.py"))

            if plugin_type in self.plugin_modules:
                plugin_instance = self.plugin_modules[plugin_type].Plugin(plugin_id, plugin_config, system_setup=system_setup)
                plugin_instance.setup_object = plugin_config
                for pin_name, pin_config in plugin_instance.pins().items():
                    if "pin" in pin_config and pin_config["pin"] and not pin_config["pin"].startswith("EXPANSION"):
                        if pin_config["pin"] == "" or pin_config["pin"] is None:
                            print(f"WARNING: pin '{pin_name}' of '{plugin_instance.instances_name}' is not set / removed")
                            del pin_config["pin"]
                self.plugin_instances.append(plugin_instance)

                return plugin_instance
        except Exception:
            print(f"ERROR: loading plugin: {plugin_id} / {plugin_config}")
            print("##################################")
            traceback.print_exc(file=sys.stdout)
            print("##################################")
            return False
        return True
