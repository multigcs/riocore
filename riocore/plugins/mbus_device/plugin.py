import glob
import json
import os

import riocore

from riocore.plugins import PluginBase

riocore_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))


class Plugin(PluginBase):
    CTYPES = {
        1: ("Read Coil Status", "input"),
        2: ("Read Input Status", "input"),
        3: ("Read Holding Registers", "input"),
        4: ("Read Input Registers ", "input"),
        5: ("Force Single Coil", "output"),
        6: ("Force Single Register", "output"),
        15: ("Force Multiple Coils", "output"),
        16: ("Preset Multiple Registers", "output"),
    }

    def setup(self):
        self.NAME = "mbus_device"
        self.INFO = "modbus device"
        self.DESCRIPTION = "modbus device"
        self.KEYWORDS = "modbus"
        self.TYPE = "base"
        self.URL = ""
        self.IMAGE = ""
        self.IMAGE_SHOW = False
        self.SIGNALS = {}
        self.PINDEFAULTS = {}
        self.OPTIONS = {}
        self.NEEDS = ["modbus"]
        self.TYPE = "base"
        board_list = []
        for jboard in glob.glob(os.path.join(os.path.dirname(__file__), "boards", "*.json")):
            board_list.append(os.path.basename(jboard).replace(".json", ""))

        self.OPTIONS.update(
            {
                "node_type": {
                    "default": "generic",
                    "type": "select",
                    "options": ["generic", *board_list],
                    "description": "device type",
                    "reload": True,
                },
                "address": {
                    "default": 1,
                    "type": int,
                    "min": 1,
                    "max": 255,
                    "description": "device address",
                },
                "priority": {
                    "default": 1,
                    "type": int,
                    "min": 1,
                    "max": 9,
                    "description": "device priority if an output value are changed / 9: higher poll rate for inputs",
                },
                "timeout": {
                    "default": 200,
                    "type": int,
                    "min": 10,
                    "max": 400,
                    "unit": "ms",
                    "description": "maximum time the client needs to answer",
                },
                "delay": {
                    "default": 200,
                    "type": int,
                    "min": 10,
                    "max": 400,
                    "unit": "ms",
                    "description": "maximum time the client needs to release the bus",
                },
            }
        )
        self.commands = {}
        self.command_ids = 0
        board = self.plugin_setup.get("node_type", self.option_default("node_type"))
        if board == "generic":
            self.PROVIDES = ["gpio"]
            self.OPTIONS.update(
                {
                    "ctype": {
                        "default": "6",
                        "type": "select",
                        "options": [f"{key}|{value[0]}" for key, value in self.CTYPES.items()],
                        "description": "comamnd / function code",
                    },
                    "vname": {
                        "default": "generic",
                        "type": str,
                        "description": "value name",
                    },
                    "register": {
                        "default": 0,
                        "type": int,
                        "min": 0,
                        "max": 65535,
                        "description": "start address of the register",
                    },
                    "values": {
                        "default": 1,
                        "type": int,
                        "min": 1,
                        "max": 16,
                        "description": "number of values",
                    },
                    "datatype": {
                        "default": "int",
                        "type": "select",
                        "options": ["int", "float", "bool"],
                        "description": "value type",
                    },
                    "scale": {
                        "default": 1.0,
                        "type": float,
                        "min": -999999.99,
                        "max": 999999.99,
                        "description": "value scale",
                    },
                    "error_values": {
                        "default": "",
                        "type": str,
                        "description": "value send on error",
                    },
                    "cmdmapping": {
                        "default": "",
                        "type": str,
                        "description": "mapping single bool outputs to int cmd value (needed for some VFD's)\nexample: reset:7, !on:6, ffw:1, rev:2",
                    },
                }
            )
            self.PINDEFAULTS = {"MODBUS": {"direction": "output", "edge": "target", "type": ["MODBUS"]}}

            command = {}
            for key in ("type", "register", "datatype", "values", "scale", "cmdmapping", "address", "priority", "delay", "timeout"):
                if key == "type":
                    command[key] = int(self.plugin_setup.get("ctype", self.option_default("ctype")))
                else:
                    command[key] = self.plugin_setup.get(key, self.option_default(key))

            name = self.plugin_setup.get("vname", self.option_default("vname"))
            self.commands = {name: command}

        else:
            board_file = os.path.join(os.path.dirname(__file__), "boards", f"{board}.json")
            if os.path.exists(board_file):
                self.IMAGE = f"boards/{board}.png"
                self.IMAGE_SHOW = True
                board_data = json.loads(open(board_file).read())
                for key in ("address", "priority", "delay", "timeout"):
                    if key in board_data:
                        self.OPTIONS[key]["default"] = board_data[key]
                self.commands = board_data["commands"]
                self.PINDEFAULTS = board_data.get("pins", {})
                for pin_data in self.PINDEFAULTS.values():
                    # print(pin_data)
                    if "GPIO" in pin_data.get("type", []):
                        self.PROVIDES = ["gpio"]
                        break

            else:
                riocore.log(f"ERROR: modbus: boardfile not found: {board_file}")

        for name, command in self.commands.items():
            datatype = command["datatype"]
            vmin = command.get("min", -99999)
            vmax = command.get("max", 99999)
            self.command_ids += 1

            direction = self.CTYPES[int(command["type"])][1]
            for vn in range(command["values"]):
                if cmdmapping := command.get("cmdmapping"):
                    for cmdsig in cmdmapping.split(","):
                        cmdname = cmdsig.split(":")[0].strip()
                        if cmdname[0] == "!":
                            cmdname = cmdname[1:]
                        self.SIGNALS[f"{name}_{cmdname}"] = {
                            "direction": direction,
                            "description": name,
                            "unit": command.get("unit", ""),
                            "format": command.get("format", ""),
                            "bool": True,
                            "display": {"section": f"mb-{board}", "title": f"{name}_{cmdname}", "min": vmin, "max": vmax},
                            "no_convert": True,
                        }
                else:
                    self.SIGNALS[f"{name}_{vn}"] = {
                        "direction": direction,
                        "description": name,
                        "unit": command.get("unit", ""),
                        "format": command.get("format", ""),
                        "bool": (datatype == "bool"),
                        "display": {"section": f"mb-{board}", "min": vmin, "max": vmax},
                        "no_convert": True,
                    }
                    if f"{name}:{vn}" in self.PINDEFAULTS:
                        del self.SIGNALS[f"{name}_{vn}"]["display"]
                        self.SIGNALS[f"{name}_{vn}"]["helper"] = True
                        self.SIGNALS[f"{name}_{vn}"]["gpio"] = True

            if direction == "input":
                self.SIGNALS[f"{name}_valid"] = {
                    "direction": "input",
                    "description": name,
                    "bool": True,
                    "validation": True,
                    "helper": True,
                    "no_convert": True,
                }
            self.SIGNALS[f"{name}_errors"] = {
                "direction": "input",
                "description": name,
                "helper": True,
                "no_convert": True,
            }

    def int2list(self, value):
        return [(value >> 8) & 0xFF, value & 0xFF]

    def list2int(self, data):
        return (data[0] << 8) + data[1]

    @classmethod
    def update_prefixes(cls, parent, instances):
        for instance in instances:
            uprefix = instance.PREFIX.replace(".", "_").upper()
            for name, command in instance.commands.items():
                if command["type"] in {2, 3, 4}:
                    command["var_prefix"] = f"*data->SIGIN_{uprefix}_{name.upper()}"
                    command["var_prefix"] = f"*data->SIGIN_{uprefix}_{name.upper()}"
                elif command["type"] in {6, 15}:
                    command["var_prefix"] = f"*data->SIGOUT_{uprefix}_{name.upper()}"
                command["stat_prefix"] = f"*data->SIGIN_{uprefix}_{name.upper()}"

    def update_pins(self, parent):
        for connected_pin in parent.get_all_plugin_pins(configured=True, prefix=self.instances_name):
            psetup = connected_pin["setup"]
            pin = connected_pin["pin"]
            # direction = connected_pin["direction"]
            # inverted = connected_pin["inverted"]
            psetup["pin"] = f"{self.PREFIX}.{pin.replace(':', '_')}"

    def device_functions_check(self, bus_master):
        output = []
        cid = 0
        for name, command in self.commands.items():
            ctype = command["type"]

            # CHECK
            output.append(f"uint8_t {self.title}_{name}_changed() {{")
            output.append(f"    // ctype ({command['type']}): {self.CTYPES[command['type']]}")
            output.append("    uint8_t changed = 0;")

            if cmdmapping := command.get("cmdmapping"):
                output.append("    // cmdmapping")
                for cmd_n, cmdsig in enumerate(cmdmapping.split(",")):
                    cmdname = cmdsig.split(":")[0].strip()
                    if cmdname[0] == "!":
                        cmdname = cmdname[1:]
                    output.append(f"    static float {name}_{cmdname}_last = 0;")
                for cmd_n, cmdsig in enumerate(cmdmapping.split(",")):
                    cmdname = cmdsig.split(":")[0].strip()
                    if cmdname[0] == "!":
                        cmdname = cmdname[1:]
                    output.append(f"    if ((float){name}_{cmdname}_last != (float){command['var_prefix']}_{cmdname.upper()}) {{")
                    output.append(f"        {name}_{cmdname}_last = (float){command['var_prefix']}_{cmdname.upper()};")
                    output.append("        changed = 1;")
                    output.append("    }")

            elif ctype in {6, 15}:
                for vn in range(command["values"]):
                    output.append(f"    static float {name}_{vn}_last = 0;")
                for vn in range(command["values"]):
                    output.append(f"    if ((float){name}_{vn}_last != (float){command['var_prefix']}_{vn}) {{")
                    output.append(f"        {name}_{vn}_last = (float){command['var_prefix']}_{vn};")
                    output.append("        changed = 1;")
                    output.append("    }")
            output.append("    return changed;")
            output.append("}")
            output.append("")
            cid += 1
        return output

    def device_functions_tx(self, bus_master):
        output = []
        cid = 0
        address = self.plugin_setup.get("address", self.option_default("address"))
        for name, command in self.commands.items():
            ctype = command["type"]
            datatype = command["datatype"]
            # TX
            output.append(f"uint8_t {self.title}_{name}_tx(uint8_t *frame) {{")
            output.append(f"    // ctype ({command['type']}): {self.CTYPES[command['type']]}")

            if cmdmapping := command.get("cmdmapping"):
                default_value = command.get("error_values") or 0
                datatype = "int"
                output.append("    // cmdmapping")
                output.append(f"    uint16_t value = {default_value};")
                for cmd_n, cmdsig in enumerate(cmdmapping.split(",")):
                    cmdname = cmdsig.split(":")[0].strip()
                    checkvalue = 1
                    if cmdname[0] == "!":
                        cmdname = cmdname[1:]
                        checkvalue = 0
                    cmdvalue = cmdsig.split(":")[1].strip()
                    if cmd_n == 0:
                        output.append(f"    if ({command['var_prefix']}_{cmdname.upper()} == {checkvalue}) {{")
                    else:
                        output.append(f"    }} else if ({command['var_prefix']}_{cmdname.upper()} == {checkvalue}) {{")
                    output.append(f"        value = {cmdvalue};")
                output.append("    }")

            if ctype in {2, 3, 4}:
                output.append("    // send request frame")
                register = self.int2list(command["register"])
                n_values = self.int2list(command["values"])
                output.append(f"    frame[0] = {address};")
                output.append(f"    frame[1] = {ctype};")
                output.append(f"    frame[2] = {register[0]};")
                output.append(f"    frame[3] = {register[1]};")
                output.append(f"    frame[4] = {n_values[0]};")
                output.append(f"    frame[5] = {n_values[1]};")
                output.append("    return 6;")

            elif ctype == 15:
                output.append("    // send data frame")
                register = self.int2list(command["register"])
                n_values = self.int2list(command["values"])
                output.append("    uint8_t bitvalues = 0;")
                for vn in range(command["values"]):
                    output.append(f"    if ({command['var_prefix']}_{vn} == 1) {{")
                    output.append(f"        bitvalues |= (1<<{vn});")
                    output.append("    }")
                output.append(f"    frame[0] = {address};")
                output.append(f"    frame[1] = {ctype};")
                output.append(f"    frame[2] = {register[0]};")
                output.append(f"    frame[3] = {register[1]};")
                output.append(f"    frame[4] = {n_values[0]};")
                output.append(f"    frame[5] = {n_values[1]};")
                output.append("    frame[6] = 1;")
                output.append("    frame[7] = bitvalues;")
                output.append("    return 8;")
            elif ctype == 6:
                output.append("    // send data frame")
                register = self.int2list(command["register"])
                n_values = self.int2list(command["values"])
                if datatype == "bool":
                    output.append("    uint16_t bitvalues = 0;")
                    for vn in range(command["values"]):
                        output.append(f"    if ({command['var_prefix']}_{vn} == 1) {{")
                        output.append(f"        bitvalues |= (1<<{vn});")
                        output.append("    }")
                elif not command.get("cmdmapping"):
                    for vn in range(command["values"]):
                        output.append(f"    uint16_t value = {command['var_prefix']}_{vn} * {command.get('scale', 1.0)};")

                output.append(f"    frame[0] = {address};")
                output.append(f"    frame[1] = {ctype};")
                output.append(f"    frame[2] = {register[0]};")
                output.append(f"    frame[3] = {register[1]};")
                if datatype == "bool":
                    output.append("    frame[4] = ((bitvalues>>8) & 0xFF);")
                    output.append("    frame[5] = (bitvalues & 0xFF);")
                else:
                    output.append("    frame[4] = ((value>>8) & 0xFF);")
                    output.append("    frame[5] = (value & 0xFF);")
                output.append("    return 6;")
            output.append("}")
            output.append("")
            cid += 1
        return output

    def device_functions_rx(self, bus_master):
        output = []
        cid = 0
        address = self.plugin_setup.get("address", self.option_default("address"))
        for name, command in self.commands.items():
            ctype = command["type"]
            datatype = command["datatype"]

            # RX
            output.append(f"void {self.title}_{name}_rx(uint8_t *frame_data, uint8_t frame_len) {{")
            output.append(f"    // ctype ({command['type']}): {self.CTYPES[command['type']]}")

            if ctype in {3, 4}:
                output.append("    uint8_t data_addr = frame_data[0];")
                output.append("    uint8_t data_type = frame_data[1];")
                output.append("    uint8_t data_len = frame_data[2];")
                output.append(f"    if (frame_len && data_addr == {address} && data_type == {ctype} && data_len == {command['values'] * 2}) {{")
                if datatype == "float":
                    output.append("        float value = 0;")
                    output.append("        uint8_t farray[] = {0, 0, frame_data[4], frame_data[3]};")
                    output.append("        memcpy((uint8_t *)&value, (uint8_t *)&farray, 4);")
                    output.append(f"        {command['var_prefix']}_0 = value * {command.get('scale', 1.0)};")
                else:
                    for vn in range(command["values"]):
                        output.append(f"        {command['var_prefix']}_{vn} = (float)((frame_data[{3 + vn * 2}]<<8) + (frame_data[{4 + vn * 2}] & 0xFF)) * {command.get('scale', 1.0)};")

                output.append(f"        {command['stat_prefix']}_VALID = 1;")
                output.append(f"        if ({command['stat_prefix']}_ERRORS > 0) {{")
                output.append(f"            {command['stat_prefix']}_ERRORS -= 1;")
                output.append("        }")
                output.append("    } else {")
                output.append(f"        {command['stat_prefix']}_ERRORS += 1;")
                output.append("    }")

            elif ctype in {2}:
                output.append("    uint8_t data_addr = frame_data[0];")
                output.append("    uint8_t data_type = frame_data[1];")
                output.append("    uint8_t data_len = frame_data[2];")
                if datatype == "bool":
                    output.append(f"    if (frame_len && data_addr == {address} && data_type == {ctype} && data_len == 1) {{")
                    for vn in range(command["values"]):
                        output.append(f"        {command['var_prefix']}_{vn} = ((frame_data[3] & (1<<{vn})) != 0);")
                else:
                    output.append(f"    if (frame_len && {address} && data_type == {ctype} && data_len == {command['values'] * 2}) {{")
                    for vn in range(command["values"]):
                        output.append(f"        {command['var_prefix']}_{vn} = (float)((frame_data[{3 + vn * 2}]<<8) + (frame_data[{4 + vn * 2}] & 0xFF)) * {command.get('scale', 1.0)};")
                output.append(f"        {command['stat_prefix']}_VALID = 1;")
                output.append(f"        if ({command['stat_prefix']}_ERRORS > 0) {{")
                output.append(f"            {command['stat_prefix']}_ERRORS -= 1;")
                output.append("        }")
                output.append("    } else {")
                output.append(f"        {command['stat_prefix']}_ERRORS += 1;")
                output.append("    }")

            elif ctype in (6, 15):
                output.append("    // check response")
                if ctype == 15:
                    output.append(f"    if (frame_len > 0 && memcmp({bus_master.instances_name}_frame_last_tx, frame_data, 6) == 0) {{")
                else:
                    output.append(f"    if (frame_len > 0 && memcmp({bus_master.instances_name}_frame_last_tx, frame_data, {bus_master.instances_name}_frame_last_tx_len) == 0) {{")
                output.append(f"        if ({command['stat_prefix']}_ERRORS > 0) {{")
                output.append(f"            {command['stat_prefix']}_ERRORS -= 1;")
                output.append("        }")
                output.append("    } else {")
                output.append(f"        {command['stat_prefix']}_ERRORS += 1;")
                output.append("    }")

            output.append("}")
            output.append("")
            cid += 1
        return output

    def device_functions(self, bus_master):
        output = []
        output.append(f"// generated by plugin: {self.NAME}")
        output.append("")
        output += self.device_functions_check(bus_master)
        output += self.device_functions_tx(bus_master)
        output += self.device_functions_rx(bus_master)
        return "\n".join(output)

    def gateware_instances(self):
        return None
