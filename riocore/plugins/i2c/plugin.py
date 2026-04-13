import os

from riocore.plugins import PluginBase

riocore_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))


class Plugin(PluginBase):
    WRITE_TYPES = {0, 5, 6, 15, 16}

    def setup(self):
        self.NAME = "i2c"
        self.INFO = "i2c bus master"
        self.DESCRIPTION = "for sensors and io-expansion"
        self.KEYWORDS = "expansion analog digital"
        self.URL = ""
        self.ORIGIN = ""
        self.TYPE = "base"
        self.VERILOGS = ["i2c_master.v"]
        self.IMAGE = ""
        self.IMAGE_SHOW = False
        self.SIGNALS = {}
        self.PINDEFAULTS = {}
        self.PROVIDES = ["i2c"]
        self.NEEDS = ["fpga"]
        self.OPTIONS = {}
        self.INTERFACE = {}
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
            "BUS:IO": {"direction": "output", "edge": "source", "bus": True, "type": ["I2C"]},
        }
        self.MAX_BITS = 16
        self.MAX_DIN = 48

    @classmethod
    def update_prefixes(cls, parent, instances):
        for instance in instances:
            instance.multiplexer = None
            instance.device_instances = []
            for connected_pin in parent.get_all_plugin_pins(configured=True, prefix=instance.instances_name):
                plugin_instance = connected_pin["instance"]
                plugin_instance.master = instance.master
                plugin_instance.PREFIX = f"{instance.master}.{plugin_instance.instances_name}"
                if plugin_instance.options.get("multiplexer") is True:
                    dev_address = plugin_instance.plugin_setup.get("address", plugin_instance.option_default("address"))
                    if instance.multiplexer is not None:
                        print(f"ERROR: {instance.instances_name}: only one multiplexer is allowed per bus")
                    instance.multiplexer = dev_address
                    continue
                instance.device_instances.append(plugin_instance)

            if not instance.device_instances:
                continue

            verilog_data = []
            verilog_data = []
            verilog_data.append("")
            verilog_data.append(f"module i2cbus_{instance.instances_name}")
            verilog_data.append("    #(parameter MAX_BITS = 64, parameter MAX_DIN = 64)")
            verilog_data.append("    (")
            verilog_data.append("        input clk,")
            for device_instance in instance.device_instances:
                for iname, iface in device_instance.INTERFACE.items():
                    direction = iface["direction"]
                    size = iface["size"]
                    if direction == "input":
                        if size == 1:
                            verilog_data.append(f"        output reg {device_instance.instances_name}_{iname} = 0,")
                        else:
                            verilog_data.append(f"        output reg [{size - 1}:0] {device_instance.instances_name}_{iname} = 0,")
                    elif direction == "output":
                        if size == 1:
                            verilog_data.append(f"        input wire {device_instance.instances_name}_{iname},")
                        else:
                            verilog_data.append(f"        input wire [{size - 1}:0] {device_instance.instances_name}_{iname},")
            verilog_data.append("        inout sda,")
            verilog_data.append("        output scl")
            verilog_data.append("    );")

            verilog_data.append("    localparam RW_WRITE = 0;")
            verilog_data.append("    localparam RW_READ = 1;")
            verilog_data.append("")

            if instance.multiplexer:
                maddr = instance.multiplexer.replace("0x", "7'h")
                verilog_data.append(f"    localparam MULTIPLEXER_ADDR = {maddr};")
                verilog_data.append("")

            for device_instance in instance.device_instances:
                if extra := device_instance.plugin_setup.get("extra"):
                    verilog_data += extra
                    verilog_data += [""]

            dev_divider_max = 0
            for dev_n, plugin_instance in enumerate(instance.device_instances):
                name = plugin_instance.instances_name
                setup = plugin_instance.plugin_setup
                dev_address = plugin_instance.plugin_setup.get("address", plugin_instance.option_default("address"))
                dev_speed = plugin_instance.plugin_setup.get("speed", plugin_instance.option_default("speed"))
                dev_divider = instance.system_setup.get("speed", 100000000) // dev_speed // 6
                dev_divider_max = max(dev_divider_max, dev_divider)
                vaddr = dev_address.replace("0x", "7'h")
                devname = f"DEVICE_{name.replace(' ', '').upper()}"
                subbus = None
                if hasattr(plugin_instance, "busid"):
                    subbus = plugin_instance.busid
                if subbus is not None:
                    verilog_data.append(f"    // device {name} on sub-bus: {subbus} ({dev_speed}Hz)")
                else:
                    verilog_data.append(f"    // device {name} ({dev_speed}Hz)")
                verilog_data.append(f"    localparam {devname} = {dev_n};")
                verilog_data.append(f"    localparam {devname}_ADDR = {vaddr};")
                verilog_data.append(f"    localparam {devname}_DIVIDER = {dev_divider};")
                if hasattr(plugin_instance, "PARAMS"):
                    for key, value in plugin_instance.PARAMS.items():
                        verilog_data.append(f"    parameter {key} = {value};")
                if hasattr(plugin_instance, "DEFINES"):
                    for entry in plugin_instance.DEFINES:
                        verilog_data.append(f"    {entry}")
                verilog_data.append("")

            dev_divider_bits = instance.clog2(dev_divider_max + 1)
            verilog_data.append(f"    localparam DIVIDER_BITS = {dev_divider_bits};")
            for dev_n, plugin_instance in enumerate(instance.device_instances):
                name = plugin_instance.instances_name
                setup = plugin_instance.plugin_setup
                lname = name.replace(" ", "").lower()
                needs_timeout = 0
                needs_delay = 0
                # total_dev_steps = instance.add_steps(setup, plugin_instance.INITS)[0] + instance.add_steps(setup, plugin_instance.STEPS)[0]
                # total_dev_steps_bits = instance.clog2(total_dev_steps + 1)
                total_dev_steps_bits = 8
                verilog_data.append(f"    reg [{total_dev_steps_bits - 1}:0] device_{lname}_step = 0;")
                for data in plugin_instance.INITS + plugin_instance.STEPS:
                    if data["mode"] == "delay":
                        ms = data.get("ms")
                        needs_delay = max(int(instance.system_setup.get("speed", 100000000) / 1000 * ms), needs_delay)
                    if data.get("until"):
                        timeout = data.get("timeout")
                        needs_timeout = max(int(instance.system_setup.get("speed", 100000000) / 1000 * timeout), needs_timeout)
                if needs_timeout:
                    bits = instance.clog2(needs_timeout + 1)
                    verilog_data.append(f"    reg device_{lname}_timeout_error = 0;")
                    verilog_data.append(f"    reg [{bits}:0] device_{lname}_timeout_cnt = 0;")
                if needs_delay:
                    bits = instance.clog2(needs_delay + 1)
                    verilog_data.append(f"    reg [{bits}:0] device_{lname}_delay_cnt = 0;")
            verilog_data.append("")

            verilog_data.append("    reg [DIVIDER_BITS-1:0] divider = 100;")
            verilog_data.append("    reg [7:0] mpx_last = 255;")
            verilog_data.append("    reg [15:0] temp = 0;")
            verilog_data.append("    reg do_init = 1;")
            verilog_data.append("    reg stop = 1;")
            verilog_data.append("    reg [7:0] device_n = 0;")
            verilog_data.append("    reg [6:0] addr = 0;")
            verilog_data.append("    reg rw = RW_WRITE;")
            verilog_data.append("    reg [4:0] bytes = 0;")
            verilog_data.append("    reg [MAX_BITS-1:0] data_out = 0;")
            verilog_data.append("    wire [MAX_DIN-1:0] data_in;")
            verilog_data.append("    reg start = 0;")
            verilog_data.append("    reg wakeup = 0;")
            verilog_data.append("    wire busy;")
            verilog_data.append("    wire error;")
            verilog_data.append("    always @(posedge clk) begin")
            verilog_data.append("")

            for device_instance in instance.device_instances:
                name = device_instance.instances_name
                setup = device_instance.plugin_setup
                lname = name.replace(" ", "").lower()
                needs_timeout = False
                needs_delay = False
                for data in device_instance.INITS + device_instance.STEPS:
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

            for dev_n, device_instance in enumerate(instance.device_instances):
                name = device_instance.instances_name
                setup = device_instance.plugin_setup
                devname = f"DEVICE_{name.replace(' ', '').upper()}"
                lname = name.replace(" ", "").lower()
                setup["name"] = name
                needs_timeout = False
                needs_delay = False
                for data in device_instance.INITS + device_instance.STEPS:
                    if data["mode"] == "delay":
                        needs_delay = True
                    if data.get("until"):
                        needs_timeout = True

                if dev_n == 0:
                    verilog_data.append(f"            if (device_n == {devname}) begin")
                else:
                    verilog_data.append(f"            end else if (device_n == {devname}) begin")
                verilog_data.append(f"                divider <= {devname}_DIVIDER;")
                verilog_data.append("")

                if needs_delay:
                    verilog_data.append(f"                // check delay counter for {name}")
                    verilog_data.append(f"                if (device_{lname}_delay_cnt > 0) begin")
                    verilog_data.append("                    device_n <= device_n + 7'd1;")
                    verilog_data.append("")
                    next_if = "end else "
                else:
                    next_if = ""

                subbus = None
                if hasattr(device_instance, "busid"):
                    subbus = device_instance.busid
                if instance.multiplexer:
                    if subbus is not None:
                        subbus_bits = 1 << int(subbus)
                    else:
                        subbus_bits = 0
                elif subbus is not None:
                    print("ERROR: i2cbus: no multiplxer configured for subbus")

                if instance.multiplexer:
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
                else:
                    verilog_data.append(f"                {next_if}if (do_init) begin")

                verilog_data.append(f"                    // init steps for {name}")
                verilog_data += instance.add_steps(device_instance, device_instance.INITS)[1]
                verilog_data.append("                end else begin")
                verilog_data.append(f"                    // loop steps for {name}")
                verilog_data += instance.add_steps(device_instance, device_instance.STEPS)[1]
                verilog_data.append("                end")
                verilog_data.append("")

            if instance.device_instances:
                verilog_data.append("            end else begin")
                verilog_data.append("                do_init <= 0;")
                verilog_data.append("                device_n <= 0;")
                verilog_data.append("            end")
            verilog_data.append("        end")
            verilog_data.append("    end")
            verilog_data.append("")
            verilog_data.append("    i2c_master #(.MAX_BITS(MAX_BITS), .MAX_DIN(MAX_DIN), .DIVIDER_BITS(DIVIDER_BITS)) i2cinst0 (")
            verilog_data.append("        .clk(clk),")
            verilog_data.append("        .sda(sda),")
            verilog_data.append("        .scl(scl),")
            verilog_data.append("        .start(start),")
            verilog_data.append("        .wakeup(wakeup),")
            verilog_data.append("        .busy(busy),")
            verilog_data.append("        .error(error),")
            verilog_data.append("        .set_divider(divider),")
            verilog_data.append("        .set_addr(addr),")
            verilog_data.append("        .set_rw(rw),")
            verilog_data.append("        .stop(stop),")
            verilog_data.append("        .set_bytes(bytes),")
            verilog_data.append("        .set_data_out(data_out),")
            verilog_data.append("        .data_in(data_in)")
            verilog_data.append("    );")
            verilog_data.append("endmodule")

            for device_instance in instance.device_instances:
                name = device_instance.instances_name
                setup = device_instance.plugin_setup
                default = setup.get("default", 0)
                expansion = setup.get("expansion", False)
                bit_n = {"input": 0, "output": 0}
                for key, ifaces in device_instance.INTERFACE.items():
                    direction = ifaces["direction"]
                    ifaces["expansion"] = expansion
                    ifaces["default"] = default
                    ifaces["bit"] = bit_n[direction]
                    # instance.INTERFACE[key] = ifaces
                    bit_n[direction] += 1

                """
                for key, ifaces in device_instance.SIGNALS.items():
                    if not expansion:
                        instance.SIGNALS[key] = ifaces
                        #if setup["subbus"]:
                        #    instance.SIGNALS[key]["device_id"] = f"{name}({setup['address']})"
                        #else:
                        #    instance.SIGNALS[key]["device_id"] = f"{name}({setup['subbus']}-{setup['address']})"
                        #instance.SIGNALS[key]["subbus"] = setup["subbus"]
                """

            instance.VERILOGS_DATA = {f"i2cbus_{instance.instances_name}.v": "\n".join(verilog_data)}

    def gateware_instances(self):
        if not self.device_instances:
            return None
        instances = self.gateware_instances_base()
        instance = instances[self.instances_name]
        instance["module"] = f"i2cbus_{self.instances_name}"
        instance_parameter = instance["parameter"]
        instance_parameter["MAX_BITS"] = self.MAX_BITS
        instance_parameter["MAX_DIN"] = self.MAX_DIN
        instance_arguments = instance["arguments"]
        for device_instance in self.device_instances:
            for key, ifaces in device_instance.INTERFACE.items():
                instance_arguments[f"{device_instance.instances_name}_{key}"] = ifaces["variable"]
        return instances

    def add_steps(self, plugin_instance, steps):
        verilog_data = []
        name = plugin_instance.instances_name
        lname = name.replace(" ", "").lower()
        dev_valid = None
        for iname, iface in plugin_instance.INTERFACE.items():
            direction = iface["direction"]
            size = iface["size"]
            if direction == "input" and iname == "valid":
                dev_valid = f"{plugin_instance.instances_name}_{iname}"

        devname = f"DEVICE_{name.replace(' ', '').upper()}"
        check_timeout = False
        dev_step = 0
        verilog_data.append(f"                    case (device_{lname}_step)")
        for data in steps:
            stype = data["mode"]
            nbytes = data.get("bytes", 1)
            size = nbytes * 8
            data_out = data.get("data_out")
            data_in = data.get("data_in")
            value = data.get("value")
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
                verilog_data.append(f"                            device_{lname}_delay_cnt <= {int(self.system_setup.get('speed', 100000000) / 1000 * ms)};")
                verilog_data.append("                        end")
                dev_step += 1

            elif stype == "wakeup":
                verilog_data.append(f"                        {dev_step}: begin")
                verilog_data.append(f"                            device_{lname}_step <= device_{lname}_step + 7'd1;")
                verilog_data.append("                            wakeup <= 1;")
                verilog_data.append("                        end")
                dev_step += 1

            elif stype == "writereg":
                self.MAX_BITS = max(self.MAX_BITS, size + 8)
                for entry in values:
                    target, value = entry
                    verilog_data.append(f"                        {dev_step}: begin")
                    if isinstance(value, str):
                        verilog_data.append(f"                            // {value} -> 0x{target:X}")
                    else:
                        verilog_data.append(f"                            // 0x{value:X} -> 0x{target:X}")
                    verilog_data.append(f"                            device_{lname}_step <= device_{lname}_step + 7'd1;")
                    verilog_data.append(f"                            addr <= {dev_addr};")
                    verilog_data.append("                            rw <= RW_WRITE;")
                    verilog_data.append(f"                            bytes <= {1 + nbytes};")
                    if big_endian:
                        print("TODO")
                    elif isinstance(value, str):
                        verilog_data.append(f"                            data_out[MAX_BITS-1:MAX_BITS-{size}-8] <= {{8'h{target:X}, {value}}};")
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
                if nbytes > 0:
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
                verilog_data.append(f"                            device_{lname}_delay_cnt <= {int(self.system_setup.get('speed', 100000000) / 1000 * 2)};")
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
                verilog_data.append(f"                            device_{lname}_delay_cnt <= {int(self.system_setup.get('speed', 100000000) / 1000 * 2)};")
                verilog_data.append("                        end")
                dev_step += 1

            elif stype in {"read", "readreg"}:
                if until:
                    check_timeout = True
                    verilog_data.append(f"                        {dev_step}: begin")
                    verilog_data.append(f"                            // {name}: {stype}: set timeout")
                    verilog_data.append(f"                            device_{lname}_step <= device_{lname}_step + 7'd1;")
                    verilog_data.append(f"                            device_{lname}_timeout_cnt <= 31'd{int(self.system_setup.get('speed', 100000000) / 1000 * timeout)};")
                    verilog_data.append(f"                            device_{lname}_timeout_error <= 1'd0;")
                    verilog_data.append("                        end")
                    dev_step += 1

                if stype == "readreg":
                    verilog_data.append(f"                        {dev_step}: begin")
                    verilog_data.append(f"                            // {name}: {stype}: set register")
                    verilog_data.append(f"                            device_{lname}_step <= device_{lname}_step + 7'd1;")
                    verilog_data.append(f"                            addr <= {dev_addr};")
                    verilog_data.append("                            rw <= RW_WRITE;")
                    verilog_data.append(f"                            bytes <= {1};")
                    verilog_data.append(f"                            data_out[MAX_BITS-1:MAX_BITS-8] <= 8'h{register:X};")
                    if stop:
                        verilog_data.append("                            stop <= 1;")
                    else:
                        verilog_data.append("                            stop <= 0;")
                    verilog_data.append("                            start <= 1;")
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
                    if stype == "readreg":
                        verilog_data.append(f"                                        device_{lname}_step <= device_{lname}_step - 7'd2;")
                    else:
                        verilog_data.append(f"                                        device_{lname}_step <= device_{lname}_step - 7'd1;")
                    verilog_data.append("                                    end")
                    verilog_data.append("                                end")
                elif data_in:
                    verilog_data += data_in
                elif var_set:
                    verilog_data.append(f"                                {data['var']} <= {var_set};")
                elif big_endian:
                    byte_list = []
                    for byte_n in range(nbytes):
                        byte_list.append(f"data_in[{byte_n * 8 + 7}:{byte_n * 8}]")
                    verilog_data.append(f"                                {data['var']} <= {{{', '.join(byte_list)}}};")
                else:
                    verilog_data.append(f"                                {data['var']} <= data_in[{size - 1}:0];")

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
        return (dev_step, verilog_data)
