from struct import unpack

from riocore.checksums import crc16
from riocore.plugins import PluginBase
from riocore.plugins.modbus import hy_vfd


class Plugin(PluginBase):
    def setup(self):
        self.ON_ERROR_CMDS = []
        self.NAME = "modbus"
        self.INFO = "generic modbus plugin"
        self.DESCRIPTION = "to read and write values (analog/digital) via modbus, also supports hy_vfd spindles"
        self.KEYWORDS = "modbus vfd spindle expansion analog digital"
        self.ORIGIN = "https://github.com/ChandulaNethmal/Implemet-a-UART-link-on-FPGA-with-verilog/tree/master"
        self.VERILOGS = ["modbus.v", "uart_baud.v", "uart_rx.v", "uart_tx.v"]
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
            },
        }
        self.OPTIONS = {
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
        self.SIGNALS = {}
        self.TYPE = "frameio"
        self.DYNAMIC_SIGNALS = True
        self.PLUGIN_CONFIG = True
        self.TIMEOUT = 200.0
        self.DELAY = 90.0
        rx_buffersize = self.plugin_setup.get("rx_buffersize", self.OPTIONS["rx_buffersize"]["default"])
        tx_buffersize = self.plugin_setup.get("tx_buffersize", self.OPTIONS["tx_buffersize"]["default"])
        if rx_buffersize < 40:
            print(f"ERROR: {self.NAME}: rx_buffersize too small: {rx_buffersize} < {40}")
            exit(1)
        if tx_buffersize < 40:
            print(f"ERROR: {self.NAME}: tx_buffersize too small: {tx_buffersize} < {40}")
            exit(1)

        if (rx_buffersize % 8) != 0:
            print(f"ERROR: {self.NAME}: rx_buffersize must be a multiple of 8: {rx_buffersize}")
            exit(1)

        if (tx_buffersize % 8) != 0:
            print(f"ERROR: {self.NAME}: tx_buffersize must be a multiple of 8: {tx_buffersize}")
            exit(1)
        vmin = 0
        vmax = 65535
        for signal_name, config in self.plugin_setup.get("config", {}).items():
            n_values = config.get("values", 0)
            ctype = config["type"]
            datatype = config.get("datatype", "int")
            if ctype == 101:
                config["instance"] = hy_vfd.hy_vfd(self.SIGNALS, signal_name, config)
                if hasattr(config["instance"], "on_error"):
                    self.ON_ERROR_CMDS += config["instance"].on_error()
            elif ctype == 201:
                self.SIGNALS[signal_name] = {
                    "direction": config["direction"],
                    "unit": config.get("unit", ""),
                    "scale": config.get("scale", 1.0),
                    "format": config.get("format", "07d"),
                    "plugin_setup": config,
                    "min": 0,
                    "max": 1,
                    "bool": True,
                    "display": {"section": "modbus", "title": signal_name.title()},
                }
            else:
                is_bool = False
                if ctype in {2, 5, 15}:
                    is_bool = True
                elif ctype == 6 and datatype == "bool":
                    is_bool = True
                    if n_values > 16:
                        print("ERROR: modbus: you can use max 16 booleans with func:6")
                if n_values > 1:
                    for vn in range(0, n_values):
                        value_name = f"{signal_name}_{vn}"
                        self.SIGNALS[value_name] = {
                            "direction": config["direction"],
                            "unit": config.get("unit", ""),
                            "scale": config.get("scale", 1.0),
                            "format": config.get("format", "07d"),
                            "plugin_setup": config,
                            "min": vmin,
                            "max": vmax,
                            "bool": is_bool,
                            "display": {"section": "modbus", "title": value_name.title()},
                        }
                        if config["direction"] == "input":
                            self.SIGNALS[f"{value_name}_valid"] = {
                                "direction": "input",
                                "bool": True,
                                "validation": True,
                                "helper": True,
                                "plugin_setup": config,
                            }
                            self.SIGNALS[f"{value_name}_errors"] = {
                                "direction": "input",
                                "validation_counter": True,
                                "format": "03d",
                                "helper": True,
                                "plugin_setup": config,
                            }
                else:
                    self.SIGNALS[signal_name] = {
                        "direction": config["direction"],
                        "unit": config.get("unit", ""),
                        "scale": config.get("scale", 1.0),
                        "format": config.get("format", "07d"),
                        "plugin_setup": config,
                        "min": vmin,
                        "max": vmax,
                        "bool": is_bool,
                        "display": {"section": "modbus", "title": signal_name.title()},
                    }
                    if config["direction"] == "input":
                        self.SIGNALS[f"{signal_name}_valid"] = {
                            "direction": "input",
                            "bool": True,
                            "validation": True,
                            "helper": True,
                            "plugin_setup": config,
                        }
                        self.SIGNALS[f"{signal_name}_errors"] = {
                            "direction": "input",
                            "validation_counter": True,
                            "format": "03d",
                            "helper": True,
                            "plugin_setup": config,
                        }

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

        for signal_name, config in self.plugin_setup.get("config", {}).items():
            n_values = config.get("values", 0)
            ctype = config["type"]
            error_values = config.get("error_values", "").strip().replace(",", " ").split()
            direction = config["direction"]
            cmd = []
            if ctype == 101:
                pass
            elif ctype == 201:
                pass
            elif direction == "output" and error_values:
                address = config["address"]
                register = self.int2list(config["register"])
                n_values = self.int2list(len(error_values))
                if config["values"] > 1:
                    if ctype == 15:
                        cmd = [address, ctype] + register + n_values + [1]
                        bitvalues = 0
                        for value in error_values:
                            if int(value) == 1:
                                bitvalues = bitvalues | (1 << vn)
                        cmd.append(bitvalues)
                    else:
                        cmd = [address, ctype] + register + n_values
                        for value in error_values:
                            cmd += self.int2list(int(value))
                else:
                    value = int(error_values[0])
                    if ctype == 5:
                        value *= 65280
                    cmd = [address, ctype] + register + self.int2list(value)

                csum = crc16()
                csum.update(cmd)
                cmd += csum.intdigest()
                self.ON_ERROR_CMDS.append(cmd)

        # add signals for the documentation if nothing is configured
        if not self.SIGNALS:
            self.SIGNALS = {
                "temperature": {"direction": "input", "unit": "°C", "scale": 0.1, "format": "0.1f"},
            }

        self.signal_active = 0
        self.signal_values = 0
        self.signal_name = None

    def cfg_info(self):
        baud = int(self.plugin_setup.get("baud", self.OPTIONS["baud"]["default"]))
        return f"{baud} baud"

    def cfggraph(self, title, gAll):
        lcports = []
        signalports = []

        addresses = []
        for signal_name, signal_defaults in self.SIGNALS.items():
            address = signal_defaults.get("plugin_setup", {}).get("address")
            if address and address not in addresses:
                addresses.append(address)

        for address in addresses:
            signalports.append(f"<device_{address}>DEVICE{address}")
            gAll.edge(f"{title}:device_{address}", f"{title}_device_{address}:conn", dir="both", color="white", fontcolor="white")
            dev_title = f"{title}_device_{address}"
            devports = []
            for signal_name, signal_defaults in self.SIGNALS.items():
                dev_address = signal_defaults.get("plugin_setup", {}).get("address")
                if dev_address != address:
                    continue
                devports.append(f"<signal_{signal_name}>{signal_name}")
                # signalports.append(f"<signal_{signal_name}>{signal_name}")
                signal_config = self.plugin_setup.get("signals", {}).get(signal_name)
                if signal_config:
                    net = signal_config.get("net")
                    function = signal_config.get("function")
                    signal_direction = self.SIGNALS.get(signal_name, {}).get("direction")
                    direction_mapping = {"input": "normal", "output": "back", "inout": "both"}
                    if function:
                        gAll.edge(f"{dev_title}:signal_{signal_name}", f"hal:{function}", dir=direction_mapping.get(signal_direction, "none"), color="white", fontcolor="white")
                        lcports.append(f"<{function}>{function}")
                    if net:
                        gAll.edge(f"{dev_title}:signal_{signal_name}", f"hal:{net}", dir=direction_mapping.get(signal_direction, "none"), color="white", fontcolor="white")
                        lcports.append(f"<{net}>{net}")

            name = self.plugin_setup.get("name", self.title)
            gAll.node(
                dev_title,
                shape="record",
                label=f"{{ {{ {'|'.join(devports)} }} | <conn>DEVICE{address} }}",
                fontsize="11pt",
                style="rounded, filled",
                fillcolor="lightblue",
                URL=f"instance:{name.replace(' ', '#')}",
            )

        return (lcports, signalports)

    def delete_sub(self, device):
        ret = False
        if "config" in self.plugin_setup:
            deletes = []
            for sub_name, sub_setup in self.plugin_setup["config"].items():
                sub_address = sub_setup.get("address")
                if f"dev-{sub_address}" == device:
                    deletes.append(sub_name)
            for sub_name in deletes:
                del self.plugin_setup["config"][sub_name]
                ret = True
        return ret

    def flow(self):
        devices = {}
        # uniq device addresses
        addresses = []
        for signal_name, signal_defaults in self.SIGNALS.items():
            address = signal_defaults.get("plugin_setup", {}).get("address")
            if address and address not in addresses:
                addresses.append(address)
        for address in addresses:
            ports = {}
            for signal_name, signal_defaults in self.SIGNALS.items():
                dev_address = signal_defaults.get("plugin_setup", {}).get("address")
                if dev_address != address:
                    continue
                ports[f"sig_{signal_name}"] = {"title": signal_name}
            devices[f"dev-{address}"] = ports
        return devices

    def gateware_instances(self):
        instances = self.gateware_instances_base()
        instance = instances[self.instances_name]
        instance["predefines"]
        instance_parameter = instance["parameter"]
        instance["arguments"]
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
        if self.ON_ERROR_CMDS:
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
                instance["predefines"].append(
                    f"                    {original_name}_TMP[{offset}:0] <= {{{', '.join(frame)}, 8'd{len(cmd)}, {self.instances_name}_frame_counter}}; // send cmd on error"
                )
                instance["predefines"].append("                end")
            instance["predefines"].append("            endcase")
        instance["predefines"].append("        end")
        instance["predefines"].append("    end else begin")
        instance["predefines"].append(f"        {original_name}_TMP <= {original_name};")
        instance["predefines"].append("    end")
        instance["predefines"].append("end")
        return instances

    def int2list(self, value):
        return [(value >> 8) & 0xFF, value & 0xFF]

    def list2int(self, data):
        return (data[0] << 8) + data[1]

    def frameio_rx(self, frame_new, frame_id, frame_len, frame_data):
        if "config" not in self.plugin_setup:
            return
        signal_name = list(self.plugin_setup["config"])[self.signal_active]
        config = self.plugin_setup["config"][signal_name]
        if config["type"] == 101:
            config["instance"].frameio_rx(frame_new, frame_id, frame_len, frame_data)
        elif frame_new:
            # print(f"rx frame {self.signal_active} {frame_id} {frame_len}: {frame_data}")

            if frame_len > 4:
                address = frame_data[0]
                ctype = frame_data[1]
                csum = crc16()
                csum.update(frame_data[:-2])
                csum_calc = csum.intdigest()
                if csum_calc != frame_data[-2:]:
                    print(f"ERROR: modbus CSUM failed {csum_calc} != {frame_data[-2:]}")
                else:
                    if self.signal_values > 1:
                        for vn in range(0, self.signal_values):
                            value_name = f"{self.signal_name}_{vn}"
                            if value_name not in self.SIGNALS:
                                print(f"ERROR: no config: {value_name}")
                            else:
                                signal_config = self.SIGNALS[value_name].get("plugin_setup", {})
                                direction = signal_config.get("direction")
                                signal_address = signal_config.get("address")
                                if address != signal_address:
                                    print(f"ERROR: wrong address {address} != {signal_address}")
                                elif direction == "input":
                                    vlen = 2
                                    if self.datatype == "float":
                                        vlen = 4
                                    start_pos = 3 + vn * vlen
                                    if ctype == 2:
                                        if frame_data[3] & (1 << vn) != 0:
                                            self.SIGNALS[value_name]["value"] = 1
                                            if direction == "input":
                                                self.SIGNALS[f"{value_name}_valid"]["value"] = 1
                                        else:
                                            self.SIGNALS[value_name]["value"] = 0
                                            if direction == "input":
                                                self.SIGNALS[f"{value_name}_valid"]["value"] = 1
                                    else:
                                        value_list = frame_data[start_pos : start_pos + vlen]
                                        if value_list and len(value_list) == vlen:
                                            vscale = self.SIGNALS[value_name]["scale"]
                                            direction = self.SIGNALS[value_name]["direction"]
                                            if self.datatype == "float" and value_list and len(value_list) == vlen:
                                                self.SIGNALS[value_name]["value"] = unpack(">f", bytearray(value_list))[0]
                                            else:
                                                self.SIGNALS[value_name]["value"] = self.list2int(value_list)
                                            if vscale:
                                                self.SIGNALS[value_name]["value"] *= vscale
                                            if direction == "input":
                                                self.SIGNALS[f"{value_name}_valid"]["value"] = 1
                    else:
                        if self.signal_name not in self.SIGNALS:
                            print(f"ERROR: no signal_config: {self.signal_name}")
                        else:
                            signal_config = self.SIGNALS[self.signal_name].get("plugin_setup", {})
                            signal_address = signal_config.get("address")
                            if address != signal_address:
                                print(f"ERROR: wrong address {address} != {signal_address}")
                            else:
                                vscale = self.SIGNALS[self.signal_name]["scale"]
                                direction = self.SIGNALS[self.signal_name]["direction"]
                                if self.datatype == "float":
                                    self.SIGNALS[self.signal_name]["value"] = unpack(">f", bytearray(frame_data[3:-2]))[0]
                                else:
                                    self.SIGNALS[self.signal_name]["value"] = self.list2int(frame_data[3:-2])

                                if vscale:
                                    self.SIGNALS[self.signal_name]["value"] *= vscale
                                if direction == "input":
                                    self.SIGNALS[f"{self.signal_name}_valid"]["value"] = 1

    def frameio_tx(self, frame_ack, frame_timeout):
        if "config" not in self.plugin_setup:
            return
        # if frame_ack:
        #    print("ACK")
        if frame_timeout:
            if self.signal_values > 1:
                for vn in range(0, self.signal_values):
                    value_name = f"{self.signal_name}_{vn}"
                    if f"{value_name}_valid" in self.SIGNALS:
                        self.SIGNALS[f"{value_name}_valid"]["value"] = 0
                        self.SIGNALS[f"{value_name}_errors"]["value"] += 1
            elif f"{self.signal_name}_valid" in self.SIGNALS:
                self.SIGNALS[f"{self.signal_name}_valid"]["value"] = 0
                self.SIGNALS[f"{self.signal_name}_errors"]["value"] += 1
        if self.signal_active < len(self.plugin_setup.get("config", {})) - 1:
            self.signal_active += 1
        else:
            self.signal_active = 0
        signal_name = list(self.plugin_setup["config"])[self.signal_active]
        config = self.plugin_setup["config"][signal_name]

        if config["type"] == 101:
            cmd = config["instance"].frameio_tx(frame_ack, frame_timeout)

        elif config["type"] == 201:
            # custom boolean command
            direction = config["direction"]
            self.delay = config.get("delay", self.DELAY) * 2
            self.timeout = config.get("timeout", self.TIMEOUT) + self.delay
            address = config["address"]
            custom_on = config["on"]
            custom_off = config["off"]
            self.signal_name = signal_name
            self.signal_address = address
            value = self.SIGNALS[signal_name]["value"]
            if value == 1:
                cmd = [address] + custom_on
            else:
                cmd = [address] + custom_off

        else:
            cmd = []
            direction = config["direction"]
            self.delay = config.get("delay", self.DELAY) * 2
            self.timeout = config.get("timeout", self.TIMEOUT) + self.delay
            address = config["address"]
            ctype = config["type"]
            self.signal_name = signal_name
            self.signal_address = address
            self.is_float = config.get("is_float", False)
            dt_default = "int"
            if self.is_float:
                dt_default = "float"
            self.datatype = config.get("datatype", dt_default)
            self.signal_values = config.get("values", 1)
            register = self.int2list(config["register"])
            n_values = self.int2list(self.signal_values)
            if direction == "output":
                if self.signal_values > 1:
                    if ctype == 15:
                        cmd = [address, ctype] + register + n_values + [1]
                        bitvalues = 0
                        for vn in range(0, self.signal_values):
                            value_name = f"{self.signal_name}_{vn}"
                            value = self.SIGNALS[value_name]["value"]
                            if value == 1:
                                bitvalues = bitvalues | (1 << vn)
                        cmd.append(bitvalues)

                    elif ctype == 6 and self.datatype == "bool":
                        cmd = [address, ctype] + register
                        bitvalues = [0, 0]
                        for vn in range(0, self.signal_values):
                            value_name = f"{self.signal_name}_{vn}"
                            value = self.SIGNALS[value_name]["value"]
                            if value == 1:
                                if vn < 8:
                                    bitvalues[1] |= 1 << vn
                                else:
                                    bitvalues[0] |= 1 << (vn - 8)
                        cmd += bitvalues

                    else:
                        cmd = [address, ctype] + register + n_values
                        for vn in range(0, self.signal_values):
                            value_name = f"{self.signal_name}_{vn}"
                            value = self.SIGNALS[value_name]["value"]
                            cmd += self.int2list(value)
                else:
                    value = self.SIGNALS[signal_name]["value"]
                    if ctype == 5:
                        value *= 65280
                    cmd = [address, ctype] + register + self.int2list(value)
            else:
                if self.datatype == "float":
                    n_values = self.int2list(self.signal_values * 2)
                    cmd = [address, ctype] + register + n_values
                else:
                    cmd = [address, ctype] + register + n_values

        csum = crc16()
        csum.update(cmd)
        csum_calc = csum.intdigest()
        frame_data = cmd + csum_calc

        # print(f"tx frame -- {len(frame_data)}: {frame_data}")

        return frame_data

    def globals_c(self):
        output = []
        output.append(f"uint8_t {self.instances_name}_signal_active = 0;")
        output.append(f"uint8_t {self.instances_name}_signal_next = 0;")
        for signal_name, signal_config in self.plugin_setup.get("config", {}).items():
            ctype = signal_config["type"]
            if ctype == 101:
                output += signal_config["instance"].globals_c(self.instances_name)
        return "\n".join(output)

    def frameio_rx_c(self):
        output = []
        output.append("    if (frame_new == 1) {")
        output.append("        uint8_t n = 0;")
        output.append("        uint8_t data_len = 0;")
        output.append("        uint8_t data_addr = frame_data[0];")
        output.append("        uint8_t data_type = frame_data[1];")
        output.append("        uint16_t crc = 0xFFFF;")
        output.append("        for (n = 0; n < frame_len - 2; n++) {")
        output.append("           crc = crc16_update(crc, frame_data[n]);")
        output.append("        }")
        output.append("        if ((crc & 0xFF) == frame_data[frame_len - 2] && (crc>>8 & 0xFF) == frame_data[frame_len - 1]) {")
        output.append(f"            switch ({self.instances_name}_signal_active) {{")
        sn = 0
        for signal_name, signal_config in self.plugin_setup.get("config", {}).items():
            direction = signal_config["direction"]
            address = signal_config["address"]
            ctype = signal_config["type"]
            vscale = signal_config.get("scale", 1.0)
            self.is_float = signal_config.get("is_float", False)
            dt_default = "int"
            if self.is_float:
                dt_default = "float"
            self.datatype = signal_config.get("datatype", dt_default)
            self.signal_values = signal_config.get("values", 1)
            self.signal_name = signal_name
            self.signal_address = address
            if ctype == 101:
                output.append(f"                case {sn}: {{")
                output += signal_config["instance"].frameio_rx_c()
                output.append("                }")
            elif direction == "input":
                output.append(f"                case {sn}: {{")
                if self.signal_values > 1:
                    output.append("                    data_len = frame_data[2];")

                    if ctype == 2:
                        output.append(f"                    // get {self.signal_values} 1bit values ({signal_name})")
                        output.append(f"                    if (data_addr == {address} && data_len == 1) {{")
                        for vn in range(0, self.signal_values):
                            value_name = f"value_{self.signal_name}_{vn}"
                            output.append(f"                        if ((frame_data[3] & (1<<{vn})) != 0) {{")
                            output.append(f"                            {value_name} = 1;")
                            output.append("                        } else {")
                            output.append(f"                            {value_name} = 0;")
                            output.append("                        }")
                            output.append(f"                        {value_name}_valid = 1;")

                    else:
                        output.append(f"                    // get {self.signal_values} 16bit values ({signal_name})")
                        output.append(f"                    if (data_addr == {address} && data_len == {self.signal_values * 2}) {{")
                        for vn in range(0, self.signal_values):
                            value_name = f"value_{self.signal_name}_{vn}"
                            output.append(f"                        {value_name} = (frame_data[{3 + vn * 2}]<<8) + (frame_data[{4 + vn * 2}] & 0xFF);")
                            if vscale:
                                output.append(f"                        {value_name} *= {vscale};")
                            output.append(f"                        {value_name}_valid = 1;")

                    output.append("                    } else {")
                    for vn in range(0, self.signal_values):
                        value_name = f"value_{self.signal_name}_{vn}"
                        output.append('                        // rtapi_print("rx error: addr or len\\n");')
                        output.append(f"                        {value_name}_errors += 1;")
                        output.append(f"                        {value_name}_valid = 0;")
                    output.append("                    }")
                else:
                    if self.datatype == "float":
                        output.append("                    // get single 32bit float value")
                        output.append("                    data_len = frame_data[2];")
                        output.append(f"                    if (data_addr == {address} && data_len == {self.signal_values * 4}) {{")
                        output.append("                        uint8_t farray[] = {frame_data[6], frame_data[5], frame_data[4], frame_data[3]};")
                        output.append(f"                        memcpy((uint8_t *)&value_{self.signal_name}, (uint8_t *)&farray, 4);")
                        if vscale:
                            output.append(f"                        value_{self.signal_name} *= {vscale};")
                        output.append(f"                        value_{self.signal_name}_valid = 1;")
                        output.append("                    } else {")
                        output.append('                        // rtapi_print("rx error: addr or len\\n");')
                        output.append(f"                        value_{self.signal_name}_errors += 1;")
                        output.append(f"                        value_{self.signal_name}_valid = 0;")
                        output.append("                    }")
                    else:
                        output.append("                    // get single 16bit value")
                        output.append("                    data_len = frame_data[2];")
                        output.append(f"                    if (data_addr == {address} && data_len == {self.signal_values * 2}) {{")
                        output.append(f"                        value_{self.signal_name} = (frame_data[{3}]<<8) + (frame_data[{4}] & 0xFF);")
                        if vscale:
                            output.append(f"                        value_{self.signal_name} *= {vscale};")
                        output.append(f"                        value_{self.signal_name}_valid = 1;")
                        output.append("                    } else {")
                        output.append('                        // rtapi_print("rx error: addr or len\\n");')
                        output.append(f"                        value_{self.signal_name}_errors += 1;")
                        output.append(f"                        value_{self.signal_name}_valid = 0;")
                        output.append("                    }")
                output.append("                    break;")
                output.append("                }")
            sn += 1
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
        output.append("    if (frame_timeout == 1) {")
        output.append(f'            // rtapi_print("rx error: timeout: %d\\n", {self.instances_name}_signal_active);')
        sn = 0
        for signal_name, signal_config in self.plugin_setup.get("config", {}).items():
            direction = signal_config["direction"]
            delay = signal_config.get("delay", self.DELAY)
            timeout = signal_config.get("timeout", self.TIMEOUT) + delay
            address = signal_config["address"]
            ctype = signal_config["type"]
            self.signal_values = signal_config.get("values", 1)
            self.signal_name = signal_name
            self.signal_address = address
            if ctype == 101:
                pass
            elif ctype == 201:
                pass
            elif direction == "input":
                register = self.int2list(signal_config["register"])
                n_values = self.int2list(self.signal_values)
                if self.signal_values > 1:
                    output.append(f"            if ({self.instances_name}_signal_active == {sn}) {{")
                    for vn in range(0, self.signal_values):
                        value_name = f"value_{self.signal_name}_{vn}"
                        output.append(f"                {value_name}_valid = 0;")
                        output.append(f"                {value_name}_errors += 1;")
                    output.append("            }")
                else:
                    output.append("            // get single 16bit value")
                    output.append(f"            if ({self.instances_name}_signal_active == {sn}) {{")
                    output.append(f"                value_{signal_name}_valid = 0;")
                    output.append(f"                value_{signal_name}_errors += 1;")
                    output.append("            }")
            sn += 1
        output.append("        }")
        output.append("")

        output.append("        // check for changes on prio values")
        for signal_name, signal_config in self.plugin_setup.get("config", {}).items():
            priority = signal_config.get("priority", 0)
            if priority > 0:
                direction = signal_config["direction"]
                signal_values = signal_config.get("values", 1)
                self.is_float = signal_config.get("is_float", False)
                dt_default = "int"
                if self.is_float:
                    dt_default = "float"
                self.datatype = signal_config.get("datatype", dt_default)
                ctype = "float"
                if self.datatype == "bool":
                    ctype = "bool"
                if direction == "output":
                    if signal_values > 1:
                        for vn in range(0, signal_values):
                            value_name = f"{signal_name}_{vn}"
                            output.append(f"        static {ctype} last_value_{value_name} = 0;")
                    else:
                        output.append(f"        static {ctype} last_value_{signal_name} = 0;")

        for prio in range(9, 0, -1):
            sn = 0
            for signal_name, signal_config in self.plugin_setup.get("config", {}).items():
                priority = signal_config.get("priority", 0)
                if prio == priority:
                    direction = signal_config["direction"]
                    ctype = signal_config["type"]
                    signal_values = signal_config.get("values", 1)
                    if direction == "output" and priority > 0:
                        if signal_values > 1:
                            priochecks = []
                            for vn in range(0, signal_values):
                                value_name = f"{signal_name}_{vn}"
                                priochecks.append(f"last_value_{value_name} != value_{value_name}")
                            output.append(f"        if ({' || '.join(priochecks)}) {{")
                            for vn in range(0, signal_values):
                                value_name = f"{signal_name}_{vn}"
                                output.append(f"            last_value_{value_name} = value_{value_name};")
                            output.append(f"            {self.instances_name}_signal_active = {sn};")
                            output.append("        } else ")
                        else:
                            output.append(f"        if (last_value_{signal_name} != value_{signal_name}) {{")
                            for vn in range(0, signal_values):
                                value_name = f"{signal_name}_{vn}"
                                output.append(f"            last_value_{signal_name} = value_{signal_name};")
                            output.append(f"            {self.instances_name}_signal_active = {sn};")
                            output.append("        } else ")

                sn += 1

        output.append("        {")
        output.append(f"            if ({self.instances_name}_signal_next < {len(self.plugin_setup.get('config', {})) - 1}) {{")
        output.append(f"                {self.instances_name}_signal_next++;")
        output.append("            } else {")
        output.append(f"                {self.instances_name}_signal_next = 0;")
        output.append("            }")
        output.append(f"            {self.instances_name}_signal_active = {self.instances_name}_signal_next;")
        output.append("        }")
        output.append("")
        output.append(f"        switch ({self.instances_name}_signal_active) {{")
        sn = 0
        for signal_name, signal_config in self.plugin_setup.get("config", {}).items():
            direction = signal_config["direction"]
            delay = signal_config.get("delay", self.DELAY)
            timeout = signal_config.get("timeout", self.TIMEOUT) + delay
            address = signal_config["address"]
            ctype = signal_config["type"]
            self.signal_values = signal_config.get("values", 1)
            self.priority = signal_config.get("priority", 0)
            self.is_float = signal_config.get("is_float", False)
            dt_default = "int"
            if self.is_float:
                dt_default = "float"
            self.datatype = signal_config.get("datatype", dt_default)
            self.signal_name = signal_name
            self.signal_address = address
            output.append(f"            case {sn}: {{")
            output.append(f"                // {signal_name}")
            output.append(f"                delay = {delay};")
            output.append(f"                timeout = {timeout};")

            if ctype == 101:
                output.append("                // handle hy_vfd")
                output += signal_config["instance"].frameio_tx_c()

            elif ctype == 201:
                # custom boolean command
                custom_on = signal_config["on"]
                custom_off = signal_config["off"]
                output.append("                // custom boolean command")
                output.append(f"                frame_data[0] = {address};")
                output.append(f"                if (value_{self.signal_name} == 1) {{")
                for bn, cbyte in enumerate(custom_on):
                    output.append(f"                    frame_data[{1 + bn}] = {cbyte};")
                output.append(f"                    frame_len = {len(custom_on) + 1};")
                output.append("                } else {")
                for bn, cbyte in enumerate(custom_off):
                    output.append(f"                    frame_data[{1 + bn}] = {cbyte};")
                output.append(f"                    frame_len = {len(custom_on) + 1};")
                output.append("                }")

            elif direction == "output":
                register = self.int2list(signal_config["register"])
                n_values = self.int2list(self.signal_values)
                if self.signal_values > 1:
                    if ctype == 15:
                        output.append("                // set 1bit values")
                        output.append(f"                frame_data[0] = {address};")
                        output.append(f"                frame_data[1] = {ctype};")
                        output.append(f"                frame_data[2] = {register[0]};")
                        output.append(f"                frame_data[3] = {register[1]};")
                        output.append(f"                frame_data[4] = {n_values[0]};")
                        output.append(f"                frame_data[5] = {n_values[1]};")
                        output.append("                frame_data[6] = 1;")
                        output.append("                uint8_t bitvalues = 0;")
                        for vn in range(0, self.signal_values):
                            value_name = f"{self.signal_name}_{vn}"
                            output.append(f"                if (value_{value_name} == 1) {{")
                            output.append(f"                    bitvalues |= (1<<{vn});")
                            output.append("                }")
                        output.append("                frame_data[7] = bitvalues;")
                        output.append("                frame_len = 8;")

                    elif ctype == 6 and self.datatype == "bool":
                        output.append("                // set 1bit values")
                        output.append(f"                frame_data[0] = {address};")
                        output.append(f"                frame_data[1] = {ctype};")
                        output.append(f"                frame_data[2] = {register[0]};")
                        output.append(f"                frame_data[3] = {register[1]};")
                        output.append("                uint8_t bitvalues[2] = {0, 0};")
                        for vn in range(0, self.signal_values):
                            value_name = f"{self.signal_name}_{vn}"
                            output.append(f"                if (value_{value_name} == 1) {{")
                            if vn < 8:
                                output.append(f"                    bitvalues[1] |= (1<<{vn});")
                            else:
                                output.append(f"                    bitvalues[0] |= (1<<{vn - 8});")

                            output.append("                }")
                        output.append("                frame_data[4] = bitvalues[0];")
                        output.append("                frame_data[5] = bitvalues[1];")
                        output.append("                frame_len = 6;")

                    else:
                        output.append("                // set 16bit values")
                        output.append(f"                frame_data[0] = {address};")
                        output.append(f"                frame_data[1] = {ctype};")
                        output.append(f"                frame_data[2] = {register[0]};")
                        output.append(f"                frame_data[3] = {register[1]};")
                        output.append(f"                frame_data[4] = {n_values[0]};")
                        output.append(f"                frame_data[5] = {n_values[1]};")
                        output.append("                frame_data[6] = 1;")
                        for vn in range(0, self.signal_values):
                            value_name = f"{self.signal_name}_{vn}"
                            output.append(f"                frame_data[{6 + vn * 2}] = (uint16_t)value_{value_name}>>8 & 0xFF;")
                            output.append(f"                frame_data[{7 + vn * 2}] = (uint16_t)value_{value_name} & 0xFF;")
                        output.append(f"                frame_len = {8 + vn * 2};")
                else:
                    if ctype == 5:
                        output.append("                // set coil value")
                    else:
                        output.append("                // set 16bit value")
                    output.append(f"                frame_data[0] = {address};")
                    output.append(f"                frame_data[1] = {ctype};")
                    output.append(f"                frame_data[2] = {register[0]};")
                    output.append(f"                frame_data[3] = {register[1]};")
                    if ctype == 5:
                        output.append(f"                if (value_{signal_name} == 1) {{")
                        output.append("                    frame_data[4] = 255;")
                        output.append("                    frame_data[5] = 0;")
                        output.append("                } else {")
                        output.append("                    frame_data[4] = 0;")
                        output.append("                    frame_data[5] = 0;")
                        output.append("                }")
                    else:
                        output.append(f"                frame_data[4] = (uint16_t)value_{signal_name}>>8 & 0xFF;")
                        output.append(f"                frame_data[5] = (uint16_t)value_{signal_name} & 0xFF;")
                    output.append("                frame_len = 6;")
            else:
                register = self.int2list(signal_config["register"])
                n_values = self.int2list(self.signal_values)
                if self.datatype == "float":
                    n_values = self.int2list(self.signal_values * 2)
                    output.append("                // request 32bit float value")
                    output.append(f"                frame_data[0] = {address};")
                    output.append(f"                frame_data[1] = {ctype};")
                    output.append(f"                frame_data[2] = {register[0]};")
                    output.append(f"                frame_data[3] = {register[1]};")
                    output.append(f"                frame_data[4] = {n_values[0]};")
                    output.append(f"                frame_data[5] = {n_values[1]};")
                    output.append("                frame_len = 6;")
                else:
                    output.append("                // request 16bit value")
                    output.append(f"                frame_data[0] = {address};")
                    output.append(f"                frame_data[1] = {ctype};")
                    output.append(f"                frame_data[2] = {register[0]};")
                    output.append(f"                frame_data[3] = {register[1]};")
                    output.append(f"                frame_data[4] = {n_values[0]};")
                    output.append(f"                frame_data[5] = {n_values[1]};")
                    output.append("                frame_len = 6;")
            output.append("                break;")
            output.append("            }")
            sn += 1
        output.append("        }")
        output.append("")
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
        output.append("        }")
        return "\n".join(output)

    def testgui_frameio_init(self, layout):
        from PyQt5.QtWidgets import (
            QHBoxLayout,
            QLabel,
            QPushButton,
            QTextEdit,
        )

        def pause_toggle():
            if self.pause:
                self.pause = False
                self.button_pause.setText("PAUSE")
            else:
                self.pause = True
                self.button_pause.setText("RESUME")

        self.addrs = []
        self.linebuffer = []
        self.pause = False

        row_layout = QHBoxLayout()
        layout.addLayout(row_layout)

        row_layout.addWidget(QLabel("Log"), stretch=1)
        self.button_pause = QPushButton("PAUSE")
        self.button_pause.clicked.connect(pause_toggle)
        row_layout.addWidget(self.button_pause, stretch=1)
        row_layout.addWidget(QLabel("Addresses (RX)"), stretch=1)

        row_layout = QHBoxLayout()
        layout.addLayout(row_layout)

        self.widget_log = QTextEdit()
        row_layout.addWidget(self.widget_log, stretch=2)

        self.widget_addrs = QTextEdit()
        row_layout.addWidget(self.widget_addrs, stretch=1)

    def testgui_frameio_clean(self, txframe):
        return txframe[:-2]

    def testgui_frameio_send(self, txframe):
        csum = crc16()
        csum.update(txframe)
        txframe += csum.intdigest()
        return txframe

    def testgui_frameio_update(self, send, frame):
        if self.pause:
            return

        if send:
            frame_tx_id = int(frame[0])
            frame_tx_len = int(frame[1])
            logline = f"> {frame_tx_id}: {' '.join(frame[2:frame_tx_len])}"
            logline = f"> {' '.join(frame[2:frame_tx_len])}"
        else:
            frame_rx_id = int(frame[1])
            frame_rx_len = int(frame[2])
            frame_data = list(reversed(frame[3 : (frame_rx_len + 3)]))[:-2]
            if frame_data:
                device_addrs = frame_data[0]
                if device_addrs not in self.addrs:
                    self.addrs.append(device_addrs)
            logline = f"< {frame_rx_id}: {' '.join(frame_data)}"
            logline = f"< {' '.join(frame_data)}"

        self.linebuffer = [logline] + self.linebuffer[:50]
        self.widget_log.setPlainText("\n".join(self.linebuffer))
        self.widget_addrs.setPlainText("\n".join(self.addrs))
