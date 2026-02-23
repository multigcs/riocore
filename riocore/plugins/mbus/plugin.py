import os
import sys

from riocore.plugins import PluginBase

riocore_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))


class Plugin(PluginBase):
    WRITE_TYPES = {0, 5, 6, 15, 16}

    def setup(self):
        self.NAME = "mbus"
        self.INFO = "modbus plugin"
        self.DESCRIPTION = "to read and write values (analog/digital) via modbus, also supports hy_vfd spindles"
        self.KEYWORDS = "modbus rtu vfd spindle expansion analog digital"
        self.URL = "https://www.modbustools.com/modbus.html#function16"
        self.ORIGIN = "https://github.com/ChandulaNethmal/Implemet-a-UART-link-on-FPGA-with-verilog/tree/master"
        self.TYPE = "base"
        self.VERILOGS = ["mbus.v", "uart_baud.v", "uart_rx.v", "uart_tx.v"]
        self.IMAGE = ""
        self.IMAGE_SHOW = False
        self.SIGNALS = {}
        self.PINDEFAULTS = {}
        self.TYPE = "frameio"
        self.PROVIDES = ["modbus"]
        self.NEEDS = ["fpga"]
        self.ON_ERROR_CMDS = []
        self.OPTIONS.update(
            {
                "baud": {
                    "default": 9600,
                    "type": int,
                    "min": 300,
                    "max": 10000000,
                    "unit": "bit/s",
                    "description": "serial baud rate",
                },
                "rx_buffersize": {
                    "default": 128,
                    "type": int,
                    "min": 32,
                    "max": 255,
                    "unit": "bits",
                    "description": "max rx buffer size",
                },
                "tx_buffersize": {
                    "default": 128,
                    "type": int,
                    "min": 32,
                    "max": 255,
                    "unit": "bits",
                    "description": "max tx buffer size",
                },
            }
        )

        rx_buffersize = self.plugin_setup.get("rx_buffersize", self.OPTIONS["rx_buffersize"]["default"])
        tx_buffersize = self.plugin_setup.get("tx_buffersize", self.OPTIONS["tx_buffersize"]["default"])
        if rx_buffersize < 40:
            print(f"ERROR: {self.NAME}: rx_buffersize too small: {rx_buffersize} < {40}")
            sys.exit(1)
        if tx_buffersize < 40:
            print(f"ERROR: {self.NAME}: tx_buffersize too small: {tx_buffersize} < {40}")
            sys.exit(1)

        if (rx_buffersize % 8) != 0:
            print(f"ERROR: {self.NAME}: rx_buffersize must be a multiple of 8: {rx_buffersize}")
            sys.exit(1)

        if (tx_buffersize % 8) != 0:
            print(f"ERROR: {self.NAME}: tx_buffersize must be a multiple of 8: {tx_buffersize}")
            sys.exit(1)
        self.INTERFACE = {
            "rxdata": {
                "size": rx_buffersize,
                "direction": "input",
            },
            "txdata": {
                "size": tx_buffersize,
                "direction": "output",
            },
        }

        self.PINDEFAULTS = {
            "rx": {"direction": "input", "edge": "target", "type": ["FPGA"]},
            "tx": {"direction": "output", "edge": "target", "type": ["FPGA"]},
            "tx_enable": {"direction": "output", "edge": "target", "type": ["FPGA"]},
            "BUS:IO": {"direction": "output", "edge": "source", "bus": True, "type": ["MODBUS"]},
        }
        self.TIMEOUT = 200.0
        self.DELAY = 90.0

    def int2list(self, value):
        return [(value >> 8) & 0xFF, value & 0xFF]

    def list2int(self, data):
        return (data[0] << 8) + data[1]

    @classmethod
    def update_prefixes(cls, parent, instances):
        for instance in instances:
            instance.device_instances = []
            for connected_pin in parent.get_all_plugin_pins(configured=True, prefix=instance.instances_name):
                plugin_instance = connected_pin["instance"]
                instance.device_instances.append(plugin_instance)
                plugin_instance.master = instance.master
                plugin_instance.PREFIX = f"{instance.master}.{plugin_instance.instances_name}"

    def globals_c(self):
        tx_buffersize = self.plugin_setup.get("tx_buffersize", self.OPTIONS["tx_buffersize"]["default"])
        output = []
        output.append(f"enum {self.instances_name}_command_ids {{")
        for device_instance in self.device_instances:
            for cid in range(device_instance.command_ids):
                output.append(f"    {self.instances_name.upper()}_{device_instance.instances_name.upper()}_{cid},")
        output.append(f"    {self.instances_name.upper()}_MAX,")
        output.append("};")
        output.append("")
        output.append(f"uint8_t {self.instances_name}_signal_active = 0;")
        output.append(f"uint8_t {self.instances_name}_frame_last_tx[{tx_buffersize // 8}];")
        output.append(f"uint8_t {self.instances_name}_frame_last_tx_len = 0;")
        output.append("")

        output.append("")
        for device_instance in self.device_instances:
            output.append(device_instance.device_functions(self))

        return "\n".join(output)

    def frameio_rx_c(self):
        output = []
        output.append(f"    // generated by plugin: {self.NAME}")
        output.append("")
        output.append("    if (frame_new == 1) {")
        output.append("        uint8_t n = 0;")
        output.append("        uint16_t crc = 0xFFFF;")
        output.append("        for (n = 0; n < frame_len - 2; n++) {")
        output.append("           crc = crc16_update(crc, frame_data[n]);")
        output.append("        }")
        output.append("        if ((crc & 0xFF) == frame_data[frame_len - 2] && (crc>>8 & 0xFF) == frame_data[frame_len - 1]) {")
        output.append(f"            switch ({self.instances_name}_signal_active) {{")

        for device_instance in self.device_instances:
            cid = 0
            for name, command in device_instance.commands.items():
                output.append(f"                case {self.instances_name.upper()}_{device_instance.instances_name.upper()}_{cid}: {{")
                output.append(f"                    {device_instance.instances_name}_{name}_rx(frame_data, frame_len);")
                output.append("                    break;")
                output.append("                }")
                cid += 1

        output.append("            }")
        output.append("        } else {")
        output.append('            // rtapi_print("ERROR: CSUM: %d|%d != %d|%d\\n", crc & 0xFF, crc>>8 & 0xFF, frame_data[frame_len - 2], frame_data[frame_len - 1]);')
        output.append("        }")
        output.append('        // rtapi_print("rx frame %i %i: ", frame_id, frame_len);')
        output.append("        // for (n = 0; n < frame_len; n++) {")
        output.append('        //     rtapi_print("%i, ", frame_data[n]);')
        output.append("        // }")
        output.append('        // rtapi_print("\\n");')
        output.append("    }")
        return "\n".join(output)

    def frameio_tx_c(self):
        output = []
        output.append(f"        // generated by plugin: {self.NAME}")
        output.append("")
        output.append("        if (frame_timeout == 1) {")
        output.append(f'            // rtapi_print("rx error: timeout: %d\\n", {self.instances_name}_signal_active);')

        output.append(f"            switch ({self.instances_name}_signal_active) {{")
        for device_instance in self.device_instances:
            cid = 0
            for name, command in device_instance.commands.items():
                timeout = device_instance.plugin_setup.get("timeout", device_instance.option_default("timeout"))
                delay = device_instance.plugin_setup.get("delay", device_instance.option_default("delay"))
                output.append(f"                case {self.instances_name.upper()}_{device_instance.instances_name.upper()}_{cid}: {{")
                output.append("                    if (frame_timeout == 1) {")
                output.append(f"                        {command['stat_prefix']}_ERRORS += 1;")
                output.append("                    }")
                output.append("                    break;")
                output.append("                }")
                cid += 1
        output.append("            }")

        output.append("        }")
        output.append("")
        output.append("        // select next frame")
        output.append("        static uint8_t signal_next = 0;")
        output.append("        static uint8_t prio_next = 0;")
        output.append("        static uint8_t prio_selection = 0;")
        output.append("        static uint8_t last_selection = 0;")
        output.append("        uint8_t prio_selected = 0;")
        output.append("")
        output.append("        if (prio_selection == 1) {")
        output.append(f"            for (uint8_t i = 0; i < {self.instances_name.upper()}_MAX; i++) {{")
        output.append(f"                if (prio_next < {self.instances_name.upper()}_MAX - 1) {{")
        output.append("                    prio_next++;")
        output.append("                } else {")
        output.append("                    prio_next = 0;")
        output.append("                }")

        for priority in range(9, 0, -1):
            for device_instance in self.device_instances:
                cid = 0
                for name, command in device_instance.commands.items():
                    ctype = command.get("type", 0)
                    device_priority = device_instance.plugin_setup.get("priority", device_instance.option_default("priority"))
                    if priority == device_priority and (ctype in self.WRITE_TYPES or priority == 9):
                        if priority == 9:
                            output.append(f"                if (last_selection != {self.instances_name.upper()}_{device_instance.instances_name.upper()}_{cid} && prio_next == {self.instances_name.upper()}_{device_instance.instances_name.upper()}_{cid}) {{")
                        else:
                            output.append(f"                if (last_selection != {self.instances_name.upper()}_{device_instance.instances_name.upper()}_{cid} && prio_next == {self.instances_name.upper()}_{device_instance.instances_name.upper()}_{cid} && {device_instance.instances_name}_{name}_changed() == 1) {{")
                        output.append(f"                    // priority: {priority}")
                        output.append(f"                    {self.instances_name}_signal_active = {self.instances_name.upper()}_{device_instance.instances_name.upper()}_{cid};")
                        output.append("                    prio_selected = 1;")
                        output.append("                    break;")
                        output.append("                }")
                    cid += 1
        output.append("            }")
        output.append("        }")
        output.append("")
        output.append("        if (prio_selected == 0) {")
        output.append(f"            if (signal_next < {self.instances_name.upper()}_MAX - 1) {{")
        output.append("                signal_next++;")
        output.append("            } else {")
        output.append("                signal_next = 0;")
        output.append("            }")
        output.append("            if (signal_next == last_selection) {")
        output.append(f"                if (signal_next < {self.instances_name.upper()}_MAX - 1) {{")
        output.append("                    signal_next++;")
        output.append("                } else {")
        output.append("                    signal_next = 0;")
        output.append("                }")
        output.append("            }")
        output.append(f"            {self.instances_name}_signal_active = signal_next;")
        output.append("            prio_selection = 1;")
        output.append("        } else {")
        output.append("            prio_selection = 0;")
        output.append("        }")
        output.append(f"        last_selection = {self.instances_name}_signal_active;")
        output.append("")
        output.append("        // build next frame")
        output.append(f"        switch ({self.instances_name}_signal_active) {{")
        for device_instance in self.device_instances:
            cid = 0
            for name, command in device_instance.commands.items():
                timeout = device_instance.plugin_setup.get("timeout", device_instance.option_default("timeout"))
                delay = device_instance.plugin_setup.get("delay", device_instance.option_default("delay"))
                output.append(f"            case {self.instances_name.upper()}_{device_instance.instances_name.upper()}_{cid}: {{")
                output.append(f"                delay = {delay};")
                output.append(f"                timeout = {timeout};")
                output.append(f"                frame_len = {device_instance.instances_name}_{name}_tx(frame_data);")
                output.append("                break;")
                output.append("            }")
                cid += 1

        output.append("        }")
        output.append("")
        output.append("        if (frame_len == 0) {")
        output.append("            delay = 0;")
        output.append("            timeout = 0;")
        output.append("        } else {")
        output.append("            uint8_t i = 0;")
        output.append("            uint16_t crc = 0xFFFF;")
        output.append("            for (i = 0; i < frame_len; i++) {")
        output.append("                crc = crc16_update(crc, frame_data[i]);")
        output.append("            }")
        output.append("            frame_data[frame_len] = crc & 0xFF;")
        output.append("            frame_data[frame_len + 1] = crc>>8 & 0xFF;")
        output.append("            frame_len += 2;")

        tx_buffersize = self.plugin_setup.get("tx_buffersize", self.OPTIONS["tx_buffersize"]["default"])
        output.append("")
        output.append("            // save last send frame to check ack")
        output.append(f"            memcpy({self.instances_name}_frame_last_tx, frame_data, {tx_buffersize // 8});")
        output.append(f"            {self.instances_name}_frame_last_tx_len = frame_len;")

        output.append("        }")
        return "\n".join(output)

    def gateware_instances(self):
        instances = self.gateware_instances_base()
        instance = instances[self.instances_name]
        instance_parameter = instance["parameter"]
        baud = int(self.plugin_setup.get("baud", self.OPTIONS["baud"]["default"]))
        instance_parameter["RX_BUFFERSIZE"] = self.plugin_setup.get("rx_buffersize", self.OPTIONS["rx_buffersize"]["default"])
        instance_parameter["TX_BUFFERSIZE"] = self.plugin_setup.get("tx_buffersize", self.OPTIONS["tx_buffersize"]["default"])
        instance_parameter["ClkFrequency"] = self.system_setup["speed"]
        instance_parameter["Baud"] = baud

        num_on_error_cmds = len(self.ON_ERROR_CMDS)
        original_name = instance["arguments"]["txdata"]
        instance["arguments"]["txdata"] = f"{original_name}_TMP"
        instance["predefines"].append(f"reg [{instance_parameter['TX_BUFFERSIZE'] - 1}:0] {original_name}_TMP;")
        instance["predefines"].append(f"reg [7:0] {self.instances_name}_cmd_num = 0;")
        instance["predefines"].append(f"reg [7:0] {self.instances_name}_frame_counter = 0;")
        instance["predefines"].append(f"reg [31:0] {self.instances_name}_cmd_counter = 0;")

        instance["predefines"].append("always @(posedge sysclk) begin")
        instance["predefines"].append("    if (INTERFACE_TIMEOUT) begin")
        instance["predefines"].append(f"        if ({self.instances_name}_cmd_counter < {self.system_setup['speed'] // 5}) begin")
        instance["predefines"].append(f"            {self.instances_name}_cmd_counter <= {self.instances_name}_cmd_counter + 32'd1;")
        instance["predefines"].append("        end else begin")
        instance["predefines"].append(f"            {self.instances_name}_cmd_counter <= 0;")
        instance["predefines"].append(f"            {self.instances_name}_frame_counter <= {self.instances_name}_frame_counter + 8'd1;")
        if num_on_error_cmds:
            instance["predefines"].append(f"            case ({self.instances_name}_cmd_num)")
            for cn, cmd in enumerate(self.ON_ERROR_CMDS):
                frame = []
                for cbyte in reversed(cmd):
                    frame.append(f"8'd{cbyte}")
                instance["predefines"].append(f"                {cn}: begin")
                if cn == num_on_error_cmds - 1:
                    instance["predefines"].append(f"                    {self.instances_name}_cmd_num <= 0;")
                else:
                    instance["predefines"].append(f"                    {self.instances_name}_cmd_num <= {cn + 1};")
                offset = ((2 + len(cmd)) * 8) - 1
                instance["predefines"].append(f"                    {original_name}_TMP[{offset}:0] <= {{{', '.join(frame)}, 8'd{len(cmd)}, {self.instances_name}_frame_counter}}; // send cmd on error")
                instance["predefines"].append("                end")
            instance["predefines"].append("            endcase")
        instance["predefines"].append("        end")
        instance["predefines"].append("    end else begin")
        instance["predefines"].append(f"        {original_name}_TMP <= {original_name};")
        instance["predefines"].append("    end")
        instance["predefines"].append("end")
        return instances
