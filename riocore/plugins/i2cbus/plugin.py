import sys
import os
import importlib

from riocore.plugins import PluginBase

plugin_path = os.path.dirname(__file__)


class Plugin(PluginBase):
    def setup(self):
        self.NAME = "i2cbus"
        self.INFO = "I2C-Bus"
        self.DESCRIPTION = ""
        self.KEYWORDS = ""
        self.ORIGIN = ""
        self.VERILOGS = ["i2c_master.v"]
        self.PINDEFAULTS = {
            "sda": {
                "direction": "inout",
                "invert": False,
                "pull": None,
            },
            "scl": {
                "direction": "output",
                "invert": False,
                "pull": None,
            },
        }

        self.devices = {
            "i2cbus_ioexp0": {
                "addr": 64,
                "type": "PCF8574",
            },
            "i2cbus_ioexp1": {
                "addr": 66,
                "type": "PCF8574",
            },
            "i2cbus_lm75": {
                "addr": "8'b10010000",
                "type": "LM75",
            },
        }
        self.INTERFACE = {}
        self.SIGNALS = {}

        for name, setup in self.devices.items():
            addr = setup["addr"]
            dtype = setup["type"]
            if os.path.isfile(os.path.join(plugin_path, "devices", f"{dtype}.py")):
                sys.path.insert(0, plugin_path)
                devlib = importlib.import_module(f".{dtype}", ".devices")
                setup["i2cdev"] = devlib.i2c_device(name, addr)
            else:
                print("ERROR: i2cdev: device '{dtype}' not found")

        verilog_data = []
        verilog_data.append("")
        verilog_data.append("module i2cbus (")
        verilog_data.append("        input clk,")
        for name, setup in self.devices.items():
            i2c_dev = setup["i2cdev"]
            for iname, iface in i2c_dev.INTERFACE.items():
                direction = iface["direction"]
                size = iface["size"]
                if direction == "input":
                    if size == 1:
                        verilog_data.append(f"        output reg {iname} = 0,")
                    else:
                        verilog_data.append(f"        output reg [{size - 1}:0] {iname} = 0,")
                elif direction == "output":
                    if size == 1:
                        verilog_data.append(f"        input wire {iname},")
                    else:
                        verilog_data.append(f"        input wire [{size - 1}:0] {iname},")
        verilog_data.append("        inout sda,")
        verilog_data.append("        output scl")
        verilog_data.append("    );")

        for name, setup in self.devices.items():
            i2c_dev = setup["i2cdev"]
            for key, value in i2c_dev.PARAMS.items():
                verilog_data.append(f"    parameter {key} = {value};")

        verilog_data.append("")
        verilog_data.append("    reg [7:0] dev_step = 0;")
        verilog_data.append("    reg do_init = 1;")
        verilog_data.append("    reg [7:0] devmode = 0;")
        verilog_data.append("    reg [7:0] last_devmode = 0;")
        verilog_data.append("    reg [7:0] addr = 0;")
        verilog_data.append("    reg rw = 0;")
        verilog_data.append("    reg [4:0] bytes = 0;")
        verilog_data.append("    reg [31:0] data_out = 0;")
        verilog_data.append("    wire [31:0] data_in;")
        verilog_data.append("    reg start = 0;")
        verilog_data.append("    wire busy;")
        verilog_data.append("    wire valid;")
        verilog_data.append("    always @(posedge clk) begin")
        verilog_data.append("        if (start == 1 && busy == 1) begin")
        verilog_data.append("            start <= 0;")
        verilog_data.append("        end else if (start == 0 && busy == 0) begin")
        verilog_data.append("")

        dev_n = 0
        for name, setup in self.devices.items():
            i2c_dev = setup["i2cdev"]

            if dev_n == 0:
                verilog_data.append(f"            if (devmode == {dev_n}) begin")
            else:
                verilog_data.append(f"            end else if (devmode == {dev_n}) begin")

            verilog_data.append("                if (do_init) begin")
            dev_step = 0
            verilog_data.append("                    case (dev_step)")
            for stype, data in i2c_dev.INITS.items():
                if stype == "write":
                    verilog_data.append(f"                        {dev_step}: begin")
                    verilog_data.append("                            dev_step <= dev_step + 1;")
                    verilog_data.append(f"                            addr <= {name.upper()}_ADDR;")
                    verilog_data.append("                            rw <= 0;")
                    verilog_data.append(f"                            bytes <= {data['bytes']};")
                    verilog_data.append(f"                            data_out <= {data['var']};")
                    verilog_data.append("                            start <= 1;")
                    verilog_data.append("                        end")
                    dev_step += 1
                elif stype == "read":
                    verilog_data.append(f"                        {dev_step}: begin")
                    verilog_data.append("                            dev_step <= dev_step + 1;")
                    verilog_data.append(f"                            addr <= {name.upper()}_ADDR;")
                    verilog_data.append("                            rw <= 1;")
                    verilog_data.append(f"                            bytes <= {data['bytes']};")
                    verilog_data.append("                            start <= 1;")
                    verilog_data.append("                        end")
                    dev_step += 1
                    verilog_data.append(f"                        {dev_step}: begin")
                    verilog_data.append("                            dev_step <= dev_step + 1;")
                    verilog_data.append("                            if (valid == 1) begin")
                    verilog_data.append(f"                                {data['var']} <= data_in;")
                    verilog_data.append("                            end")
                    verilog_data.append("                        end")
                    dev_step += 1
            verilog_data.append("                        default: begin")
            verilog_data.append("                            dev_step <= 0;")
            verilog_data.append("                            devmode <= devmode + 1;")
            verilog_data.append("                        end")
            verilog_data.append("                    endcase")
            verilog_data.append("")

            verilog_data.append("                end else begin")
            dev_step = 0
            verilog_data.append("                    case (dev_step)")
            for stype, data in i2c_dev.STEPS.items():
                if stype == "write":
                    verilog_data.append(f"                        {dev_step}: begin")
                    verilog_data.append("                            dev_step <= dev_step + 1;")
                    verilog_data.append(f"                            addr <= {name.upper()}_ADDR;")
                    verilog_data.append("                            rw <= 0;")
                    verilog_data.append(f"                            bytes <= {data['bytes']};")
                    verilog_data.append(f"                            data_out <= {data['var']};")
                    verilog_data.append("                            start <= 1;")
                    verilog_data.append("                        end")
                    dev_step += 1
                elif stype == "read":
                    verilog_data.append(f"                        {dev_step}: begin")
                    verilog_data.append("                            dev_step <= dev_step + 1;")
                    verilog_data.append(f"                            addr <= {name.upper()}_ADDR;")
                    verilog_data.append("                            rw <= 1;")
                    verilog_data.append(f"                            bytes <= {data['bytes']};")
                    verilog_data.append("                            start <= 1;")
                    verilog_data.append("                        end")
                    dev_step += 1
                    verilog_data.append(f"                        {dev_step}: begin")
                    verilog_data.append("                            dev_step <= dev_step + 1;")
                    verilog_data.append("                            if (valid == 1) begin")
                    verilog_data.append(f"                                {data['var']} <= data_in;")
                    verilog_data.append("                            end")
                    verilog_data.append("                        end")
                    dev_step += 1
            verilog_data.append("                        default: begin")
            verilog_data.append("                            dev_step <= 0;")
            verilog_data.append("                            devmode <= devmode + 1;")
            verilog_data.append("                        end")
            verilog_data.append("                    endcase")
            verilog_data.append("")
            verilog_data.append("                end")
            verilog_data.append("")

            dev_n += 1

        verilog_data.append("            end else begin")
        verilog_data.append("                do_init <= 0;")
        verilog_data.append("                devmode <= 0;")
        verilog_data.append("            end")
        verilog_data.append("        end")
        verilog_data.append("    end")
        verilog_data.append("")
        verilog_data.append("    i2c_master i2cinst0 (")
        verilog_data.append("        .clk(clk),")
        verilog_data.append("        .sda(sda),")
        verilog_data.append("        .scl(scl),")
        verilog_data.append("        .start(start),")
        verilog_data.append("        .busy(busy),")
        verilog_data.append("        .valid(valid),")
        verilog_data.append("        .set_addr(addr),")
        verilog_data.append("        .set_rw(rw),")
        verilog_data.append("        .set_bytes(bytes),")
        verilog_data.append("        .set_data_out(data_out),")
        verilog_data.append("        .data_in(data_in)")
        verilog_data.append("    );")
        verilog_data.append("endmodule")

        for name, setup in self.devices.items():
            i2c_dev = setup["i2cdev"]
            self.INTERFACE.update(i2c_dev.INTERFACE)
            self.SIGNALS.update(i2c_dev.SIGNALS)

        self.VERILOGS_DATA = {"i2cbus.v": "\n".join(verilog_data)}

    def convert(self, signal_name, signal_setup, value):
        for name, setup in self.devices.items():
            if signal_name.startswith(name):
                i2c_dev = setup["i2cdev"]
                if hasattr(i2c_dev, "convert"):
                    return i2c_dev.convert(signal_name, signal_setup, value)
        return value


    def convert_c(self, signal_name, signal_setup):
        for name, setup in self.devices.items():
            if signal_name.startswith(name):
                i2c_dev = setup["i2cdev"]
                if hasattr(i2c_dev, "convert_c"):
                    return i2c_dev.convert_c(signal_name, signal_setup)
        return ""


