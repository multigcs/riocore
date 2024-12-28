import glob
import sys
from copy import deepcopy
import os
import importlib

from riocore.plugins import PluginBase

plugin_path = os.path.dirname(__file__)


class Plugin(PluginBase):
    def clog2(self, x):
        """Ceiling of log2"""
        if x <= 0:
            raise ValueError("domain error")
        return (x-1).bit_length()
    
    def setup(self):
        self.NAME = "i2cbus"
        self.INFO = "I2C-Bus"
        self.DESCRIPTION = """
I2C-Bus - supports multiple busses with multiple devices per bus

sub-busses via multiplexer (pca9548) are also supported
        """
        self.GRAPH = """
graph LR;
    FPGA-->Bus0;
    Bus0-->Device0-->Device1..;
    FPGA-->Bus1..;
    Bus1..-->Device2-->Device3..;
    Bus1..-->Multiplexer0-->Device4-->Device5..;
    Multiplexer0-->Device6-->Device7..;
        """
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
            "multiplexer": {
                "default": "",
                "type": "select",
                "options": ["", "0x70", "0x71", "0x72", "0x73", "0x74", "0x75", "0x76", "0x77"],
                "description": "Sub-Bus multiplexer address (pca9548)",
            },
        }

        self.config = self.plugin_setup.get("config", {})
        self.devices = deepcopy(self.config.get("devices", {}))
        self.multiplexer = self.plugin_setup.get("multiplexer", self.OPTIONS["multiplexer"]["default"])
        self.PLUGIN_CONFIG = True
        self.INTERFACE = {}
        self.SIGNALS = {}

        self.MAX_BITS = 16

        self.DESCRIPTION += "\n\nDevices:\n"
        for device_path in sorted(glob.glob(os.path.join(plugin_path, "devices", "*", "__init__.py"))):
            device_name = os.path.basename(os.path.dirname(device_path))
            self.DESCRIPTION += f"* [{device_name}](devices/{device_name}.py)\n"

        if not self.devices:
            return

        sys.path.insert(0, plugin_path)
        failed_devices = []
        for name, setup in self.devices.items():
            setup["name"] = name
            dtype = setup["type"]
            if os.path.isfile(os.path.join(plugin_path, "devices", dtype, "__init__.py")):
                devlib = importlib.import_module(f".{dtype}", ".devices")
                setup["i2cdev"] = devlib.i2c_device(setup, self.system_setup)
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

        verilog_data.append("    localparam RW_WRITE = 0;")
        verilog_data.append("    localparam RW_READ = 1;")
        verilog_data.append("")

        if self.multiplexer:
            maddr = self.multiplexer.replace("0x", "7'h")
            verilog_data.append(f"    localparam MULTIPLEXER_ADDR = {maddr};")
            verilog_data.append("")

        for name, setup in self.devices.items():
            extra = setup.get("extra")
            if extra:
                verilog_data += extra
                verilog_data += [""]

        for dev_n, name in enumerate(self.devices):
            setup = self.devices[name]
            setup["name"] = name
            i2c_dev = setup["i2cdev"]
            subbus = setup.get("subbus", "none")
            vaddr = i2c_dev.addr.replace("0x", "7'h")
            devname = f"DEVICE_{name.replace(' ', '').upper()}"
            if subbus != "none":
                verilog_data.append(f"    // device {name} on sub-bus: {subbus}")
            else:
                verilog_data.append(f"    // device {name}")
            verilog_data.append(f"    localparam {devname} = {dev_n};")
            verilog_data.append(f"    localparam {devname}_ADDR = {vaddr};")
            for key, value in i2c_dev.PARAMS.items():
                verilog_data.append(f"    parameter {key} = {value};")
            verilog_data.append("")

        for name, setup in self.devices.items():
            lname = name.replace(" ", "").lower()
            i2c_dev = setup["i2cdev"]

            needs_timeout = 0
            needs_delay = 0

            for data in i2c_dev.INITS + i2c_dev.STEPS:
                if data["mode"] == "delay":
                    ms = data.get("ms")
                    needs_delay = max(int(self.system_setup.get('speed', 50000000) / 1000 * ms), needs_delay)
                if data.get("until"):
                    timeout = data.get("timeout")
                    needs_timeout = max(int(self.system_setup.get('speed', 50000000) / 1000 * timeout), needs_timeout)
            verilog_data.append(f"    reg [7:0] device_{lname}_step = 0;")
            if needs_timeout:
                bits = self.clog2(needs_timeout + 1)
                verilog_data.append(f"    reg device_{lname}_timeout_error = 0;")
                verilog_data.append(f"    reg [{bits}:0] device_{lname}_timeout_cnt = 0;")
            if needs_delay:
                bits = self.clog2(needs_delay + 1)
                verilog_data.append(f"    reg [{bits}:0] device_{lname}_delay_cnt = 0;")

        verilog_data.append("")

        verilog_data.append("    reg [7:0] mpx_last = 255;")
        verilog_data.append("    reg [15:0] temp = 0;")
        verilog_data.append("    reg do_init = 1;")
        verilog_data.append("    reg stop = 1;")
        verilog_data.append("    reg [7:0] device_n = 0;")
        verilog_data.append("    reg [6:0] addr = 0;")
        verilog_data.append("    reg rw = RW_WRITE;")
        verilog_data.append("    reg [4:0] bytes = 0;")
        verilog_data.append("    reg [MAX_BITS-1:0] data_out = 0;")
        verilog_data.append("    wire [31:0] data_in;")
        verilog_data.append("    reg start = 0;")
        verilog_data.append("    reg wakeup = 0;")
        verilog_data.append("    wire busy;")
        verilog_data.append("    wire error;")
        verilog_data.append("    always @(posedge clk) begin")
        verilog_data.append("")

        for name, setup in self.devices.items():
            lname = name.replace(" ", "").lower()
            i2c_dev = setup["i2cdev"]
            needs_timeout = False
            needs_delay = False
            for data in i2c_dev.INITS + i2c_dev.STEPS:
                if data["mode"] == "delay":
                    needs_delay = True
                if data.get("until"):
                    needs_timeout = True
            if needs_timeout:
                verilog_data.append(f"        // decrease and check timeout counter for {name}")
                verilog_data.append(f"        if (device_{lname}_timeout_cnt == 0) begin")
                verilog_data.append(f"            device_{lname}_timeout_error <= 1'd1;")
                verilog_data.append("        end else begin")
                verilog_data.append(f"            device_{lname}_timeout_cnt <= device_{lname}_timeout_cnt - 1'd1;")
                verilog_data.append("        end")
                verilog_data.append("")
            if needs_delay:
                verilog_data.append(f"        // decrease delay counter for {name}")
                verilog_data.append(f"        if (device_{lname}_delay_cnt > 0) begin")
                verilog_data.append(f"            device_{lname}_delay_cnt <= device_{lname}_delay_cnt - 1'd1;")
                verilog_data.append("        end")
                verilog_data.append("")

        verilog_data.append("        if (wakeup == 1 && busy == 1) begin")
        verilog_data.append("            wakeup <= 0;")
        verilog_data.append("        end else if (start == 1 && busy == 1) begin")
        verilog_data.append("            start <= 0;")
        verilog_data.append("        end else if (start == 0 && busy == 0) begin")
        verilog_data.append("")

        dev_n = 0
        for name, setup in self.devices.items():
            devname = f"DEVICE_{name.replace(' ', '').upper()}"
            lname = name.replace(" ", "").lower()
            setup["name"] = name
            i2c_dev = setup["i2cdev"]
            subbus = setup.get("subbus", "none")
            needs_timeout = False
            needs_delay = False
            for data in i2c_dev.INITS + i2c_dev.STEPS:
                if data["mode"] == "delay":
                    needs_delay = True
                if data.get("until"):
                    needs_timeout = True

            if dev_n == 0:
                verilog_data.append(f"            if (device_n == {devname}) begin")
            else:
                verilog_data.append(f"            end else if (device_n == {devname}) begin")
            verilog_data.append("")

            if needs_delay:
                verilog_data.append(f"                // check delay counter for {name}")
                verilog_data.append(f"                if (device_{lname}_delay_cnt > 0) begin")
                verilog_data.append("                    device_n <= device_n + 7'd1;")
                verilog_data.append("")
                next_if = "end else "
            else:
                next_if = ""

            if self.multiplexer:
                if subbus != "none" and int(subbus) > 7:
                    print(f"ERROR: i2cbus: subbus {subbus} not in range: 0-7")
                if subbus == "none":
                    subbus_bits = 0
                else:
                    subbus_bits = 1 << int(subbus)
            elif subbus != "none":
                print("ERROR: i2cbus: no multiplxer configured for subbus")

            if self.multiplexer:
                verilog_data.append(f"                // check selected multiplexer port for {name}")
                verilog_data.append(f"                {next_if}if (mpx_last != 8'd{subbus_bits}) begin")
                verilog_data.append(f"                    mpx_last <= 8'd{subbus_bits};")
                verilog_data.append("")
                verilog_data.append("                    addr <= MULTIPLEXER_ADDR;")
                verilog_data.append("                    rw <= RW_WRITE;")
                verilog_data.append("                    bytes <= 1;")
                verilog_data.append(f"                    data_out[MAX_BITS-1:MAX_BITS-8] <= {subbus_bits};")
                verilog_data.append("                    stop <= 1;")
                verilog_data.append("                    start <= 1;")
                verilog_data.append("")

            verilog_data.append("                end else if (do_init) begin")
            verilog_data.append(f"                    // init steps for {name}")
            verilog_data += self.add_steps(setup, i2c_dev.INITS)
            verilog_data.append("                end else begin")
            verilog_data.append(f"                    // loop steps for {name}")
            verilog_data += self.add_steps(setup, i2c_dev.STEPS)
            verilog_data.append("                end")
            verilog_data.append("")

            dev_n += 1

        verilog_data.append("            end else begin")
        verilog_data.append("                do_init <= 0;")
        verilog_data.append("                device_n <= 0;")
        verilog_data.append("            end")
        verilog_data.append("        end")
        verilog_data.append("    end")
        verilog_data.append("")
        verilog_data.append("    i2c_master #(.DIVIDER(DIVIDER), .MAX_BITS(MAX_BITS)) i2cinst0 (")
        verilog_data.append("        .clk(clk),")
        verilog_data.append("        .sda(sda),")
        verilog_data.append("        .scl(scl),")
        verilog_data.append("        .start(start),")
        verilog_data.append("        .wakeup(wakeup),")
        verilog_data.append("        .busy(busy),")
        verilog_data.append("        .error(error),")
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
        lname = name.replace(" ", "").lower()
        i2c_dev = setup["i2cdev"]
        subbus = setup.get("subbus", "none")
        dev_valid = None
        for iname, iface in i2c_dev.INTERFACE.items():
            direction = iface["direction"]
            size = iface["size"]
            if direction == "input" and iname.endswith("_valid"):
                dev_valid = iname

        devname = f"DEVICE_{name.replace(' ', '').upper()}"
        check_timeout = False
        dev_step = 0
        verilog_data.append(f"                    case (device_{lname}_step)")
        for data in steps:
            stype = data["mode"]
            nbytes = data.get("bytes", 1)
            size = nbytes * 8
            data_out = setup.get("data_out")
            data_in = setup.get("data_in")
            value = setup.get("value")
            value = data.get("value", value)
            values = data.get("values")
            stop = data.get("stop", True)
            var_set = data.get("var_set")
            big_endian = data.get("big_endian", False)
            register = data.get("register")
            dev_addr = data.get("addr", f"{devname}_ADDR")
            comment = data.get("comment")
            timeout = data.get("timeout", 100)
            until = data.get("until")
            ms = data.get("ms")
            self.MAX_BITS = max(self.MAX_BITS, size)
            verilog_data.append(f"                        // {name}: {stype}")
            if comment:
                verilog_data.append(f"                        // {comment}")

            if stype == "delay":
                verilog_data.append(f"                        {dev_step}: begin")
                verilog_data.append(f"                            device_{lname}_step <= device_{lname}_step + 7'd1;")
                verilog_data.append(f"                            device_{lname}_delay_cnt <= {int(self.system_setup.get('speed', 50000000) / 1000 * ms)};")
                verilog_data.append("                        end")
                dev_step += 1

            elif stype == "wakeup":
                verilog_data.append(f"                        {dev_step}: begin")
                verilog_data.append(f"                            device_{lname}_step <= device_{lname}_step + 7'd1;")
                verilog_data.append("                            wakeup <= 1;")
                verilog_data.append("                        end")
                dev_step += 1

            elif stype == "readreg":
                verilog_data.append(f"                        {dev_step}: begin")
                verilog_data.append(f"                            device_{lname}_step <= device_{lname}_step + 7'd1;")
                verilog_data.append(f"                            addr <= {dev_addr};")
                verilog_data.append("                            rw <= RW_WRITE;")
                verilog_data.append(f"                            bytes <= {1};")
                verilog_data.append(f"                            data_out[MAX_BITS-1:MAX_BITS-8] <= 8'h{register:X};")
                verilog_data.append("                            stop <= 0;")
                verilog_data.append("                            start <= 1;")
                verilog_data.append("                        end")
                dev_step += 1
                verilog_data.append(f"                        {dev_step}: begin")
                verilog_data.append(f"                            device_{lname}_step <= device_{lname}_step + 7'd1;")
                verilog_data.append(f"                            addr <= {dev_addr};")
                verilog_data.append("                            rw <= RW_READ;")
                verilog_data.append(f"                            bytes <= {nbytes};")
                verilog_data.append("                            stop <= 1;")
                verilog_data.append("                            start <= 1;")
                verilog_data.append("                        end")
                dev_step += 1
                verilog_data.append(f"                        {dev_step}: begin")
                verilog_data.append(f"                            // {name}: {stype}: check for error / return variable")
                verilog_data.append(f"                            device_{lname}_step <= device_{lname}_step + 7'd1;")
                verilog_data.append("                            if (error == 0) begin")

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
                    verilog_data.append(f"                            device_{lname}_step <= device_{lname}_step + 7'd1;")
                    verilog_data.append(f"                            addr <= {dev_addr};")
                    verilog_data.append("                            rw <= RW_WRITE;")
                    verilog_data.append(f"                            bytes <= {1 + nbytes};")
                    if big_endian:
                        print("TODO")
                    else:
                        verilog_data.append(f"                            data_out[MAX_BITS-1:MAX_BITS-{size}-8] <= {{8'h{target:X}, {size}'h{value:X}}};")
                    verilog_data.append("                            stop <= 1;")
                    verilog_data.append("                            start <= 1;")
                    verilog_data.append("                        end")
                    dev_step += 1

            elif stype == "write":
                verilog_data.append(f"                        {dev_step}: begin")
                verilog_data.append(f"                            device_{lname}_step <= device_{lname}_step + 7'd1;")
                verilog_data.append(f"                            addr <= {dev_addr};")
                verilog_data.append("                            rw <= RW_WRITE;")
                verilog_data.append(f"                            bytes <= {nbytes};")
                if data_out:
                    verilog_data += data_out
                elif value is not None:
                    verilog_data.append(f"                            data_out[MAX_BITS-1:MAX_BITS-{size}] <= {value};")
                else:
                    verilog_data.append(f"                            data_out[MAX_BITS-1:MAX_BITS-{size}] <= {data['var']};")
                if stop:
                    verilog_data.append("                            stop <= 1;")
                else:
                    verilog_data.append("                            stop <= 0;")
                verilog_data.append("                            start <= 1;")
                verilog_data.append("                        end")
                dev_step += 1

            elif stype == "lcd":
                verilog_data.append(f"                        {dev_step}: begin")
                verilog_data.append("                            // set ")
                verilog_data.append(f"                            temp <= {data['var']};")
                verilog_data.append(f"                            device_{lname}_step <= device_{lname}_step + 7'd1;")
                verilog_data.append("                        end")
                dev_step += 1
                for extra in [
                    {"mode": "write", "value": "{4'h8 | temp[14:12], 4'd8}", "bytes": 1},
                    {"mode": "write", "value": "{4'h8 | temp[14:12], 4'd12}", "bytes": 1},
                    {"mode": "write", "value": "{4'h8 | temp[14:12], 4'd8}", "bytes": 1},
                    {"mode": "write", "value": "{temp[11:8], 4'd8}", "bytes": 1},
                    {"mode": "write", "value": "{temp[11:8], 4'd12}", "bytes": 1},
                    {"mode": "write", "value": "{temp[11:8], 4'd8}", "bytes": 1},
                ]:
                    verilog_data.append(f"                        {dev_step}: begin")
                    verilog_data.append("                            // pos ")
                    verilog_data.append(f"                            device_{lname}_step <= device_{lname}_step + 7'd1;")
                    verilog_data.append(f"                            addr <= {dev_addr};")
                    verilog_data.append("                            rw <= RW_WRITE;")
                    verilog_data.append("                            bytes <= 1;")
                    verilog_data.append(f"                            data_out[MAX_BITS-1:MAX_BITS-8] <= {extra['value']};")
                    verilog_data.append("                            stop <= 1;")
                    verilog_data.append("                            start <= 1;")
                    verilog_data.append("                        end")
                    dev_step += 1
                verilog_data.append(f"                        {dev_step}: begin")
                verilog_data.append(f"                            device_{lname}_step <= device_{lname}_step + 7'd1;")
                verilog_data.append(f"                            device_{lname}_delay_cnt <= {int(self.system_setup.get('speed', 50000000) / 1000 * 2)};")
                verilog_data.append("                        end")
                dev_step += 1

                verilog_data.append("                                // char")
                for extra in [
                    {"mode": "write", "value": "{temp[7:4], 4'd9}", "bytes": 1},
                    {"mode": "write", "value": "{temp[7:4], 4'd13}", "bytes": 1},
                    {"mode": "write", "value": "{temp[7:4], 4'd9} ", "bytes": 1},
                    {"mode": "write", "value": "{temp[3:0], 4'd9}", "bytes": 1},
                    {"mode": "write", "value": "{temp[3:0], 4'd13}", "bytes": 1},
                    {"mode": "write", "value": "{temp[3:0], 4'd9}", "bytes": 1},
                ]:
                    verilog_data.append(f"                        {dev_step}: begin")
                    verilog_data.append("                            // char ")
                    verilog_data.append(f"                            device_{lname}_step <= device_{lname}_step + 7'd1;")
                    verilog_data.append(f"                            addr <= {dev_addr};")
                    verilog_data.append("                            rw <= RW_WRITE;")
                    verilog_data.append("                            bytes <= 1;")
                    verilog_data.append(f"                            data_out[MAX_BITS-1:MAX_BITS-8] <= {extra['value']};")
                    verilog_data.append("                            stop <= 1;")
                    verilog_data.append("                            start <= 1;")
                    verilog_data.append("                        end")
                    dev_step += 1

                verilog_data.append(f"                        {dev_step}: begin")
                verilog_data.append(f"                            device_{lname}_step <= device_{lname}_step + 7'd1;")
                verilog_data.append(f"                            device_{lname}_delay_cnt <= {int(self.system_setup.get('speed', 50000000) / 1000 * 2)};")
                verilog_data.append("                        end")
                dev_step += 1

            elif stype == "read":
                if until:
                    check_timeout = True
                    verilog_data.append(f"                        {dev_step}: begin")
                    verilog_data.append(f"                            // {name}: {stype}: set timeout")
                    verilog_data.append(f"                            device_{lname}_step <= device_{lname}_step + 7'd1;")
                    verilog_data.append(f"                            device_{lname}_timeout_cnt <= 31'd{int(self.system_setup.get('speed', 50000000) / 1000 * timeout)};")
                    verilog_data.append(f"                            device_{lname}_timeout_error <= 1'd0;")
                    verilog_data.append("                        end")
                    dev_step += 1

                verilog_data.append(f"                        {dev_step}: begin")
                verilog_data.append(f"                            // {name}: {stype}: request the data")
                verilog_data.append(f"                            device_{lname}_step <= device_{lname}_step + 7'd1;")
                verilog_data.append(f"                            addr <= {dev_addr};")
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
                    verilog_data.append(f"                            device_{lname}_step <= device_{lname}_step + 7'd1;")
                    verilog_data.append(f"                            // {name}: {stype}: check for error / return variable")

                verilog_data.append("                            if (error == 0) begin")
                if until:
                    verilog_data.append(f"                                // {name}: {stype}: check data and wait for match")
                    verilog_data.append(f"                                if ({until}) begin")
                    verilog_data.append(f"                                    device_{lname}_step <= device_{lname}_step + 7'd1;")
                    verilog_data.append("                                end else begin")
                    verilog_data.append(f"                                    if (device_{lname}_timeout_error) begin")
                    verilog_data.append(f"                                        // {name}: {stype}: on timeout, jump to next device")
                    verilog_data.append(f"                                        device_{lname}_step <= 255;")
                    verilog_data.append("                                    end else begin")
                    verilog_data.append(f"                                        // {name}: {stype}: repeat last read")
                    verilog_data.append("                                        device_n <= device_n + 7'd1;")
                    verilog_data.append(f"                                        device_{lname}_step <= device_{lname}_step - 7'd1;")
                    verilog_data.append("                                    end")
                    verilog_data.append("                                end")
                elif data_in:
                    verilog_data += data_in
                elif var_set:
                    verilog_data.append(f"                                {data['var']} <= {var_set};")
                else:
                    verilog_data.append(f"                                {data['var']} <= data_in[{size-1}:0];")

                if until:
                    verilog_data.append("                            end else begin")
                    verilog_data.append(f"                                // {name}: {stype}: on error, jump to next device")
                    verilog_data.append(f"                                device_{lname}_step <= 255;")
                    verilog_data.append("                            end")
                else:
                    verilog_data.append("                            end")

                verilog_data.append("                        end")
                dev_step += 1
            verilog_data.append("")
        verilog_data.append("                        default: begin")
        verilog_data.append(f"                            device_{lname}_step <= 0;")
        verilog_data.append("                            device_n <= device_n + 7'd1;")
        if dev_valid:
            if check_timeout:
                verilog_data.append(f"                            {dev_valid} <= ~error && ~device_{lname}_timeout_error;")
            else:
                verilog_data.append(f"                            {dev_valid} <= ~error;")

        verilog_data.append("                        end")
        verilog_data.append("                    endcase")
        verilog_data.append("")
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
