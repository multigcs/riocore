import glob
import sys
from copy import deepcopy
import os
import importlib

from riocore.plugins import PluginBase

plugin_path = os.path.dirname(__file__)


class Plugin(PluginBase):
    def setup(self):
        self.NAME = "i2cbus"
        self.INFO = "I2C-Bus"
        self.DESCRIPTION = "I2C-Bus - supports multiple busses with multiple devices per bus"
        self.KEYWORDS = "adc temperatur voltage current"
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

        self.OPTIONS = {
            "speed": {
                "default": 100000,
                "type": int,
                "min": 100,
                "max": 50000000,
                "unit": "Hz",
                "description": "I2C-Clockspeed",
            },
        }

        self.config = self.plugin_setup.get("config", {})
        self.devices = deepcopy(self.config.get("devices", {}))
        self.PLUGIN_CONFIG = True
        self.INTERFACE = {}
        self.SIGNALS = {}

        self.MAX_BITS = 64
        self.MAX_BITS = 8

        self.DESCRIPTION += "\n\nDevices:\n"
        for device_path in sorted(glob.glob(os.path.join(plugin_path, "devices", "*.py"))):
            device_name = os.path.basename(device_path).replace(".py", "")
            if not device_name.startswith("_"):
                self.DESCRIPTION += f"* [{device_name}](devices/{device_name}.py)\n"

        if not self.devices:
            return

        sys.path.insert(0, plugin_path)
        failed_devices = []
        for name, setup in self.devices.items():
            setup["name"] = name
            dtype = setup["type"]
            if os.path.isfile(os.path.join(plugin_path, "devices", f"{dtype}.py")):
                devlib = importlib.import_module(f".{dtype}", ".devices")
                setup["i2cdev"] = devlib.i2c_device(setup)
            else:
                print(f"ERROR: i2cdev: device '{dtype}' not found")
                failed_devices.append(name)
        for dev in failed_devices:
            del self.devices[dev]

        verilog_data = []
        verilog_data.append("")
        verilog_data.append(f"module i2cbus_{self.instances_name}")
        verilog_data.append("    #(parameter DIVIDER = 42, parameter MAX_BITS = 64)")
        verilog_data.append("    (")
        verilog_data.append("        input clk,")
        for name, setup in self.devices.items():
            setup["name"] = name
            i2c_dev = setup["i2cdev"]
            for iname, iface in i2c_dev.INTERFACE.items():
                direction = iface["direction"]
                signed = iface.get("signed", False)
                size = iface["size"]

                signed_str = ""
                if signed:
                    signed_str = " signed"

                if direction == "input":
                    if size == 1:
                        verilog_data.append(f"        output reg{signed_str} {iname} = 0,")
                    else:
                        verilog_data.append(f"        output reg{signed_str} [{size - 1}:0] {iname} = 0,")
                elif direction == "output":
                    if size == 1:
                        verilog_data.append(f"        input wire{signed_str} {iname},")
                    else:
                        verilog_data.append(f"        input wire{signed_str} [{size - 1}:0] {iname},")
        verilog_data.append("        inout sda,")
        verilog_data.append("        output scl")
        verilog_data.append("    );")

        verilog_data.append("    localparam RW_WRITE = 0;")
        verilog_data.append("    localparam RW_READ = 1;")

        for name, setup in self.devices.items():
            extra = setup.get("extra")
            if extra:
                verilog_data += extra
                verilog_data += [""]

        for name, setup in self.devices.items():
            setup["name"] = name
            i2c_dev = setup["i2cdev"]
            vaddr = i2c_dev.addr.replace("0x", "7'h")
            verilog_data.append(f"    localparam {name.upper()}_ADDR = {vaddr};")
            for key, value in i2c_dev.PARAMS.items():
                verilog_data.append(f"    parameter {key} = {value};")

        verilog_data.append("")
        verilog_data.append("    reg [7:0] dev_step = 0;")
        verilog_data.append("    reg do_init = 1;")
        verilog_data.append("    reg stop = 1;")
        verilog_data.append("    reg [7:0] devmode = 0;")
        verilog_data.append("    reg [7:0] last_devmode = 0;")
        verilog_data.append("    reg [6:0] addr = 0;")
        verilog_data.append("    reg rw = RW_WRITE;")
        verilog_data.append("    reg [4:0] bytes = 0;")
        verilog_data.append("    reg [MAX_BITS-1:0] data_out = 0;")
        verilog_data.append("    wire [31:0] data_in;")
        verilog_data.append("    reg [31:0] delay_cnt = 2700000;")
        verilog_data.append("    reg start = 0;")
        verilog_data.append("    wire busy;")
        verilog_data.append("    wire valid;")
        verilog_data.append("    always @(posedge clk) begin")
        verilog_data.append("        if (delay_cnt > 0) begin")
        verilog_data.append("            delay_cnt <= delay_cnt - 1;")
        verilog_data.append("        end else if (start == 1 && busy == 1) begin")
        verilog_data.append("            start <= 0;")
        verilog_data.append("        end else if (start == 0 && busy == 0) begin")
        verilog_data.append("")

        dev_n = 0
        for name, setup in self.devices.items():
            setup["name"] = name
            i2c_dev = setup["i2cdev"]

            if dev_n == 0:
                verilog_data.append(f"            if (devmode == {dev_n}) begin")
            else:
                verilog_data.append(f"            end else if (devmode == {dev_n}) begin")
            verilog_data.append("                if (do_init) begin")
            verilog_data += self.add_steps(setup, i2c_dev.INITS)
            verilog_data.append("                end else begin")
            verilog_data += self.add_steps(setup, i2c_dev.STEPS)
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
        verilog_data.append("    i2c_master #(.DIVIDER(DIVIDER), .MAX_BITS(MAX_BITS)) i2cinst0 (")
        verilog_data.append("        .clk(clk),")
        verilog_data.append("        .sda(sda),")
        verilog_data.append("        .scl(scl),")
        verilog_data.append("        .start(start),")
        verilog_data.append("        .busy(busy),")
        verilog_data.append("        .valid(valid),")
        verilog_data.append("        .set_addr(addr),")
        verilog_data.append("        .set_rw(rw),")
        verilog_data.append("        .stop(stop),")
        verilog_data.append("        .set_bytes(bytes),")
        verilog_data.append("        .set_data_out(data_out),")
        verilog_data.append("        .data_in(data_in)")
        verilog_data.append("    );")
        verilog_data.append("endmodule")

        for name, setup in self.devices.items():
            setup["name"] = name
            setup["plugin_setup"] = self.plugin_setup
            i2c_dev = setup["i2cdev"]
            default = setup.get("default", 0)
            expansion = setup.get("expansion", False)
            bit_n = {"input": 0, "output": 0}
            for key, ifaces in i2c_dev.INTERFACE.items():
                direction = ifaces["direction"]
                ifaces["expansion"] = expansion
                ifaces["default"] = default
                ifaces["bit"] = bit_n[direction]
                self.INTERFACE[key] = ifaces
                bit_n[direction] += 1

            for key, ifaces in i2c_dev.SIGNALS.items():
                if not expansion:
                    self.SIGNALS[key] = ifaces

        self.VERILOGS_DATA = {f"i2cbus_{self.instances_name}.v": "\n".join(verilog_data)}

    def add_steps(self, setup, steps):
        verilog_data = []
        name = setup["name"]
        dev_step = 0
        verilog_data.append("                    case (dev_step)")
        for data in steps:
            stype = data["mode"]
            nbytes = data.get("bytes", 1)
            size = nbytes * 8
            data_out = setup.get("data_out")
            data_in = setup.get("data_in")
            value = data.get("value")
            values = data.get("values")
            stop = data.get("stop", True)
            var_set = data.get("var_set")
            big_endian = data.get("big_endian", False)
            register = data.get("register")
            until = data.get("until")
            ms = data.get("ms")
            self.MAX_BITS = max(self.MAX_BITS, size)
            verilog_data.append(f"                        // {stype}")
            if stype == "delay":
                verilog_data.append(f"                        {dev_step}: begin")
                verilog_data.append("                            dev_step <= dev_step + 7'd1;")
                verilog_data.append(f"                            delay_cnt <= {int(self.system_setup.get('speed', 50000000) / 1000 * ms)};")
                verilog_data.append("                        end")
                dev_step += 1

            elif stype == "readreg":
                verilog_data.append(f"                        {dev_step}: begin")
                verilog_data.append("                            dev_step <= dev_step + 7'd1;")
                verilog_data.append(f"                            addr <= {name.upper()}_ADDR;")
                verilog_data.append("                            rw <= RW_WRITE;")
                verilog_data.append(f"                            bytes <= {1};")
                verilog_data.append(f"                            data_out[{self.MAX_BITS-1}:{self.MAX_BITS-8}] <= 8'h{register:X};")
                verilog_data.append("                            stop <= 0;")
                verilog_data.append("                            start <= 1;")
                verilog_data.append("                        end")
                dev_step += 1
                verilog_data.append(f"                        {dev_step}: begin")
                verilog_data.append("                            dev_step <= dev_step + 7'd1;")
                verilog_data.append(f"                            addr <= {name.upper()}_ADDR;")
                verilog_data.append("                            rw <= RW_READ;")
                verilog_data.append(f"                            bytes <= {nbytes};")
                verilog_data.append("                            stop <= 1;")
                verilog_data.append("                            start <= 1;")
                verilog_data.append("                        end")
                dev_step += 1
                verilog_data.append(f"                        {dev_step}: begin")
                verilog_data.append("                            dev_step <= dev_step + 7'd1;")
                verilog_data.append("                            if (valid == 1) begin")
                if data_in:
                    verilog_data += data_in
                elif var_set:
                    verilog_data.append(f"                                {data['var']} <= {var_set};")
                else:
                    if big_endian:
                        byte_list = []
                        for byte_n in range(nbytes):
                            byte_list.append(f"data_in[{byte_n*8+7}:{byte_n*8}]")
                        verilog_data.append(f"                                {data['var']} <= {{{', '.join(byte_list)}}};")
                    else:
                        verilog_data.append(f"                                {data['var']} <= data_in[{size-1}:0];")
                verilog_data.append("                            end")
                verilog_data.append("                        end")
                dev_step += 1

            elif stype == "writereg":
                self.MAX_BITS = max(self.MAX_BITS, size + 8)
                for entry in values:
                    target, value = entry
                    verilog_data.append(f"                        {dev_step}: begin")
                    verilog_data.append(f"                            // 0x{value:X} -> 0x{target:X}")
                    verilog_data.append("                            dev_step <= dev_step + 7'd1;")
                    verilog_data.append(f"                            addr <= {name.upper()}_ADDR;")
                    verilog_data.append("                            rw <= RW_WRITE;")
                    verilog_data.append(f"                            bytes <= {nbytes};")
                    if big_endian:
                        print("TODO")
                    else:
                        verilog_data.append(f"                            data_out[{self.MAX_BITS-1}:{self.MAX_BITS-size-8}] <= {{8'h{target:X}, {size}'h{value:X}}};")
                    verilog_data.append("                            stop <= 1;")
                    verilog_data.append("                            start <= 1;")
                    verilog_data.append("                        end")
                    dev_step += 1

            elif stype == "write":
                verilog_data.append(f"                        {dev_step}: begin")
                verilog_data.append("                            dev_step <= dev_step + 7'd1;")
                verilog_data.append(f"                            addr <= {name.upper()}_ADDR;")
                verilog_data.append("                            rw <= RW_WRITE;")
                verilog_data.append(f"                            bytes <= {nbytes};")
                if data_out:
                    verilog_data += data_out
                elif value:
                    verilog_data.append(f"                            data_out[{self.MAX_BITS-1}:{self.MAX_BITS-size}] <= {value};")
                else:
                    verilog_data.append(f"                            data_out[{self.MAX_BITS-1}:{self.MAX_BITS-size}] <= {data['var']};")
                if stop:
                    verilog_data.append("                            stop <= 1;")
                else:
                    verilog_data.append("                            stop <= 0;")
                verilog_data.append("                            start <= 1;")
                verilog_data.append("                        end")
                dev_step += 1
            elif stype == "read":
                verilog_data.append(f"                        {dev_step}: begin")
                verilog_data.append("                            dev_step <= dev_step + 7'd1;")
                verilog_data.append(f"                            addr <= {name.upper()}_ADDR;")
                verilog_data.append("                            rw <= RW_READ;")
                verilog_data.append(f"                            bytes <= {nbytes};")
                if stop:
                    verilog_data.append("                            stop <= 1;")
                else:
                    verilog_data.append("                            stop <= 0;")
                verilog_data.append("                            start <= 1;")
                verilog_data.append("                        end")
                dev_step += 1
                verilog_data.append(f"                        {dev_step}: begin")
                if not until:
                    verilog_data.append("                            dev_step <= dev_step + 7'd1;")
                verilog_data.append("                            if (valid == 1) begin")
                if until:
                    verilog_data.append(f"                                if ({until}) begin")
                    verilog_data.append("                                    dev_step <= dev_step + 7'd1;")
                    verilog_data.append("                                end else begin")
                    verilog_data.append("                                    dev_step <= dev_step - 7'd1;")
                    verilog_data.append("                                end")
                elif data_in:
                    verilog_data += data_in
                elif var_set:
                    verilog_data.append(f"                                {data['var']} <= {var_set};")
                else:
                    verilog_data.append(f"                                {data['var']} <= data_in[{size-1}:0];")

                if until:
                    verilog_data.append("                            end else begin")
                    verilog_data.append("                                dev_step <= dev_step + 7'd1;")
                    verilog_data.append("                            end")
                else:
                    verilog_data.append("                            end")

                verilog_data.append("                        end")
                dev_step += 1
            verilog_data.append("")
        verilog_data.append("                        default: begin")
        verilog_data.append("                            dev_step <= 0;")
        verilog_data.append("                            devmode <= devmode + 7'd1;")
        verilog_data.append("                        end")
        verilog_data.append("                    endcase")
        return verilog_data

    def gateware_instances(self):
        instances = self.gateware_instances_base()
        instance = instances[self.instances_name]
        instance["module"] = f"i2cbus_{self.instances_name}"
        instance_parameter = instance["parameter"]
        freq = int(self.plugin_setup.get("speed", self.OPTIONS["speed"]["default"]))
        divider = self.system_setup["speed"] // freq // 6
        instance_parameter["DIVIDER"] = divider
        instance_parameter["MAX_BITS"] = self.MAX_BITS
        return instances

    def convert(self, signal_name, signal_setup, value):
        for name, setup in self.devices.items():
            setup["name"] = name
            if signal_name.startswith(name):
                i2c_dev = setup["i2cdev"]
                if hasattr(i2c_dev, "convert"):
                    return i2c_dev.convert(signal_name, signal_setup, value)
        return value

    def convert_c(self, signal_name, signal_setup):
        for name, setup in self.devices.items():
            setup["name"] = name
            if signal_name.startswith(name):
                i2c_dev = setup["i2cdev"]
                if hasattr(i2c_dev, "convert_c"):
                    return i2c_dev.convert_c(signal_name, signal_setup)
        return ""
