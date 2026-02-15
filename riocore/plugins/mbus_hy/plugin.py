import os

from riocore.plugins import PluginBase

riocore_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))


class Plugin(PluginBase):
    HYVFD_MAX_TRYS = 100
    HYVFD_ON_ERROR_CMDS = [
        [0x03, 0x01, 0x08],  # stop spindle on error
    ]
    HYVFD_CALC_KEYS = {
        "max_freq": {"scale": 0.01, "unit": "Hz"},
        "base_freq": {"scale": 0.01, "unit": "Hz"},
        "freq_lower_limit": {"scale": 0.01, "unit": "Hz"},
        "rated_motor_voltage": {"scale": 0.1, "unit": "V"},
        "rated_motor_current": {"scale": 0.1, "unit": "A"},
        "rpm_at_50hz": {"scale": 1.0, "unit": "RPM"},
        "rated_motor_rev": {"scale": 1.0, "unit": "RPM"},
        "speed_fb": {
            "scale": 1.0,
            "unit": "RPM",
            "helper": False,
            "display": {
                "section": "status",
                "group": "Spindle",
                "title": "RPM",
                "type": "meter",
                "min": 0,
                "max": 24000,
                "size": 250,
                "region": [[0, 6000, "gray"], [6000, 20000, "green"], [20000, 24000, "red"]],
            },
        },
        "speed_fb_rps": {"scale": 1.0, "unit": "RPS"},
        "at_speed": {"scale": 1.0, "bool": True, "helper": False, "display": {"section": "status", "group": "Spindle", "title": "AT-Speed"}},
        "error_count": {"scale": 1.0, "helper": False, "display": {"section": "vfd", "title": "Errors", "format": "d"}},
        "hycomm_ok": {"scale": 1.0, "bool": True},
    }
    HYVFD_SIGNALS = {
        "speed_command": {"direction": "output", "unit": "RPM", "net": "spindle.0.speed-out-abs", "display": {"section": "vfd", "title": "Speed-Set", "format": "d", "min": -24000, "max": 24000}},
        "speed_fb_rps": {"direction": "input", "unit": "RPM", "net": "spindle.0.speed-in", "display": {"type": "none"}},
        "spindle_at_speed_tolerance": {"direction": "output", "unit": "", "net": "", "helper": True},
        "spindle_forward": {"direction": "output", "bool": True, "net": "spindle.0.forward", "display": {"type": "none"}},
        "spindle_reverse": {"direction": "output", "bool": True, "net": "spindle.0.reverse", "display": {"type": "none"}},
        "spindle_on": {"direction": "output", "bool": True, "net": "spindle.0.on", "display": {"type": "none"}},
        "at_speed": {"direction": "input", "bool": True, "net": "spindle.0.at-speed", "display": {"type": "none"}},
    }
    HYVFD_DATA = {}
    HYVFD_CONFIG_REGISTER = {
        4: {"done": False, "value": 0, "try": 0, "name": ""},
        5: {"done": False, "value": 0, "try": 0, "name": ""},
        11: {"done": False, "value": 0, "try": 0, "name": ""},
        141: {"done": False, "value": 0, "try": 0, "name": ""},
        142: {"done": False, "value": 0, "try": 0, "name": ""},
        # 143: {"done": False, "value": 0, "try": 0, "name": ""},
        144: {"done": False, "value": 0, "try": 0, "name": ""},
    }
    HYVFD_CONFIG_REGISTER_SETUP = True
    HYVFD_STATUS_READ = False
    HYVFD_SET_SPEED = 0
    HYVFD_COMMAND = 0
    HYVFD_STATUS_REGISTER_ACTIVE = 0
    HYVFD_STATUS_REGISTER = {
        0: {"done": False, "value": 0, "name": "frq_set", "scale": 0.01, "unit": "Hz", "priority": 1},
        1: {"done": False, "value": 0, "name": "frq_get", "scale": 0.01, "unit": "Hz", "priority": 1},
        2: {"done": False, "value": 0, "name": "ampere", "scale": 0.01, "unit": "A", "priority": 0, "display": {"section": "vfd", "title": "Ampere", "format": "0.1f"}},
        3: {"done": False, "value": 0, "name": "rpm", "scale": 1.0, "unit": "RPM", "priority": 0, "display": {"section": "vfd", "title": "RPM", "format": "d"}},
        4: {"done": False, "value": 0, "name": "dc_volt", "scale": 0.1, "unit": "V", "priority": 0, "display": {"section": "vfd", "title": "DC", "format": "0.1f"}},
        5: {"done": False, "value": 0, "name": "ac_volt", "scale": 0.1, "unit": "V", "priority": 0, "display": {"section": "vfd", "title": "AC", "format": "0.1f"}},
        # 6: {"done": False, "value": 0, "name": "condition", "scale": 1.0, "unit": ""},
        # 7: {"done": False, "value": 0, "name": "temp", "scale": 1.0, "unit": ""},
    }

    def setup(self):
        self.NAME = "mbus_hy"
        self.COMPONENT = "mbus_hy"
        self.INFO = "modbus hy vfd"
        self.DESCRIPTION = "modbus hy vfd"
        self.KEYWORDS = "modbus"
        self.TYPE = "base"
        self.PLUGIN_TYPE = "modbus"
        self.URL = ""
        self.IMAGE = ""
        self.IMAGE_SHOW = False
        self.SIGNALS = {}
        self.PINDEFAULTS = {}
        self.OPTIONS = {}
        self.NEEDS = ["modbus"]
        self.TYPE = "base"
        self.OPTIONS.update(
            {
                "address": {
                    "default": 1,
                    "type": int,
                    "min": 1,
                    "max": 255,
                    "description": "device address",
                },
                "priority": {
                    "default": 9,
                    "type": int,
                    "min": 1,
                    "max": 9,
                    "description": "device priority",
                },
                "timeout": {
                    "default": 160,
                    "type": int,
                    "min": 10,
                    "max": 400,
                    "description": "device timeout",
                },
                "delay": {
                    "default": 100,
                    "type": int,
                    "min": 10,
                    "max": 400,
                    "description": "device delay",
                },
            }
        )
        self.commands = {}
        self.command_ids = 1
        self.IMAGE = "image.png"
        self.IMAGE_SHOW = True
        self.PINDEFAULTS = {"MODBUS": {"direction": "output", "edge": "target", "pos": [145, 340], "type": ["MODBUS"]}}
        self.commands = {
            "vfd": {
                "values": 0,
                "direction": "output",
            }
        }

        self.SIGNALS = self.HYVFD_SIGNALS

        for name, data in self.HYVFD_CALC_KEYS.items():
            value_name = name
            self.SIGNALS[value_name] = {
                "direction": "input",
                "net": data.get("net", ""),
                "unit": data.get("unit", ""),
                "bool": data.get("bool", False),
                "helper": data.get("helper", True),
                "display": data.get("display", {}),
                "scale": 1.0,
                "format": ".2f",
                "no_convert": True,
            }

        for register, data in self.HYVFD_STATUS_REGISTER.items():
            value_name = data["name"]
            self.SIGNALS[value_name] = {
                "direction": "input",
                "net": data.get("net", ""),
                "unit": data.get("unit", ""),
                "scale": 1.0,
                "format": "7.2f",
                "display": data.get("display", {}),
                "helper": True,
                "no_convert": True,
            }

        for name, command in self.commands.items():
            self.SIGNALS[f"{name}_errors"] = {
                "direction": "input",
                "description": name,
                "helper": True,
                "no_convert": True,
            }

        # set predefined halpins/net
        if "signals" not in self.plugin_setup:
            self.plugin_setup["signals"] = {}
        for key, value in self.SIGNALS.items():
            if net := value.get("net"):
                if key not in self.plugin_setup["signals"]:
                    self.plugin_setup["signals"][key] = {}
                self.plugin_setup["signals"][key]["net"] = net

    def int2list(self, value):
        return [(value >> 8) & 0xFF, value & 0xFF]

    def list2int(self, data):
        return (data[0] << 8) + data[1]

    @classmethod
    def update_prefixes(cls, parent, instances):
        for instance in instances:
            for name, command in instance.commands.items():
                command["stat_prefix"] = f"*data->SIGIN_{instance.title.upper()}_{name.upper()}"

    def predefines(self):
        num_config_registers = len(self.HYVFD_CONFIG_REGISTER)
        num_status_registers = len(self.HYVFD_STATUS_REGISTER)
        output = []
        output.append(f"uint8_t {self.instances_name}_register_setup = 1;")
        output.append(f"uint8_t {self.instances_name}_status_read = 0;")
        output.append(f"uint8_t {self.instances_name}_set_speed = 0;")
        output.append(f"uint8_t {self.instances_name}_command = 0;")
        output.append(f"uint8_t {self.instances_name}_status_register_active = 0;")
        output.append("")
        output.append("typedef struct {;")
        output.append("    float value;")
        output.append("    uint8_t num;")
        output.append("    uint8_t done;")
        output.append("    uint8_t try;")
        output.append(f"}} {self.instances_name}_config_register_t;")
        output.append("")
        output.append("typedef struct {;")
        output.append("    float value;")
        output.append("    uint8_t num;")
        output.append("    uint8_t done;")
        output.append("    uint8_t try;")
        output.append(f"}} {self.instances_name}_status_register_t;")
        output.append("")
        output.append(f"{self.instances_name}_config_register_t {self.instances_name}_config_register[{num_config_registers}] = {{")
        for register, data in self.HYVFD_CONFIG_REGISTER.items():
            output.append(f"    {{0.0, {register}, 0, 0}},")
        output.append("};")
        output.append(f"{self.instances_name}_status_register_t {self.instances_name}_status_register[{num_status_registers}] = {{")
        for register, data in self.HYVFD_STATUS_REGISTER.items():
            output.append(f"    {{0.0, {register}, 0, 0}},")
        output.append("};")
        output.append(f"uint16_t {self.instances_name}_speed_last = 0xFFFF;")
        output.append(f"int8_t {self.instances_name}_status_last = 0xFF;")
        output.append("")
        return "\n".join(output)

    def func_tx(self):
        address = self.plugin_setup.get("address", self.option_default("address"))
        utitle = self.title.upper()
        num_config_registers = len(self.HYVFD_CONFIG_REGISTER)
        num_config_registers = len(self.HYVFD_STATUS_REGISTER)
        output = []
        output.append(f"uint8_t {self.title}_vfd_tx(uint8_t *frame_data) {{")
        output.append("    uint8_t n = 0;")
        output.append("    uint8_t frame_len = 0;")
        output.append("    static uint8_t init_timer = 0;")
        output.append("")
        output.append("    if (*data->sys_enable == 0 && init_timer++ > 10) {")
        output.append("        init_timer = 0;")
        output.append(f"        {self.instances_name}_register_setup = 1;")
        output.append("        for (n = 0; n < 6; n++) {")
        output.append(f"            {self.instances_name}_config_register[n].try = 0;")
        output.append("        }")
        output.append("    }")
        output.append(f"    if ({self.instances_name}_register_setup == 1) {{")
        output.append(f"        {self.instances_name}_register_setup = 0;")
        output.append(f"        for (n = 0; n < {num_config_registers}; n++) {{")
        output.append(f"            if ({self.instances_name}_config_register[n].done == 0 && {self.instances_name}_config_register[n].try < 50) {{")
        output.append(f"                {self.instances_name}_config_register[n].try += 1;")
        output.append(f"                {self.instances_name}_register_setup = 1;")
        output.append(f"                frame_data[0] = {address};")
        output.append("                frame_data[1] = 0x01;")
        output.append("                frame_data[2] = 0x03;")
        output.append(f"                frame_data[3] = {self.instances_name}_config_register[n].num;")
        output.append("                frame_data[4] = 0x00;")
        output.append("                frame_data[5] = 0x00;")
        output.append("                frame_len = 6;")
        output.append("                break;")
        output.append("            }")
        output.append("        }")
        output.append("    } else {")
        output.append(f"        if ({self.instances_name}_command < 2) {{")
        output.append(f"            {self.instances_name}_command += 1;")
        output.append("        } else {")
        output.append(f"            {self.instances_name}_command = 0;")
        output.append("        }")
        output.append(f"        if ({self.instances_name}_command == 0) {{")
        output.append("            // do status")
        output.append(f"            if ({self.instances_name}_status_register_active < {num_config_registers - 2}) {{")
        output.append(f"                {self.instances_name}_status_register_active += 1;")
        output.append("            } else {")
        output.append(f"                {self.instances_name}_status_register_active = 0;")
        output.append("            }")
        output.append(f"            frame_data[0] = {address};")
        output.append("            frame_data[1] = 0x04;")
        output.append("            frame_data[2] = 0x03;")
        output.append(f"            frame_data[3] = {self.instances_name}_status_register[{self.instances_name}_status_register_active].num;")
        output.append("            frame_data[4] = 0x00;")
        output.append("            frame_data[5] = 0x00;")
        output.append("            frame_len = 6;")
        output.append(f"        }} else if ({self.instances_name}_command == 1) {{")
        output.append("            // set speed")
        output.append("            float freq_comp = 0;")
        output.append("            float hz_per_rpm = 0;")
        output.append(f"            if (*data->SIGIN_{utitle}_RATED_MOTOR_REV > 0.0) {{")
        output.append(f"               hz_per_rpm = *data->SIGIN_{utitle}_MAX_FREQ / *data->SIGIN_{utitle}_RATED_MOTOR_REV;")
        output.append("            }")
        output.append(f"            float value =  fabs((*data->SIGOUT_{utitle}_SPEED_COMMAND + freq_comp) * hz_per_rpm);")
        output.append(f"            if (value > *data->SIGIN_{utitle}_MAX_FREQ) {{")
        output.append(f"                value = *data->SIGIN_{utitle}_MAX_FREQ;")
        output.append("            }")
        output.append(f"            if (value < *data->SIGIN_{utitle}_FREQ_LOWER_LIMIT) {{")
        output.append(f"                value = *data->SIGIN_{utitle}_FREQ_LOWER_LIMIT;")
        output.append("            }")
        output.append("            uint16_t value_int = value * 100.0;")
        output.append(f"            if (value_int != {self.instances_name}_speed_last) {{")
        output.append(f"                *data->SIGIN_{utitle}_AT_SPEED = 0;")
        output.append(f"                frame_data[0] = {address};")
        output.append("                frame_data[1] = 0x05;")
        output.append("                frame_data[2] = 0x02;")
        output.append("                frame_data[3] = value_int>>8 & 0xFF;")
        output.append("                frame_data[4] = value_int & 0xFF;")
        output.append("                frame_len = 5;")
        output.append("            }")
        output.append(f"        }} else if ({self.instances_name}_command == 2) {{")
        output.append(f"            frame_data[0] = {address};")
        output.append("            frame_data[1] = 0x03;")
        output.append("            frame_data[2] = 0x01;")
        output.append(f"            if (*data->SIGOUT_{utitle}_SPINDLE_ON == 0) {{")
        output.append("                // STOP;")
        output.append("                frame_data[3] = 0x08;")
        output.append(f"            }} else if (*data->SIGOUT_{utitle}_SPINDLE_FORWARD == 1) {{")
        output.append("                // FWD;")
        output.append("                frame_data[3] = 0x01;")
        output.append(f"            }} else if (*data->SIGOUT_{utitle}_SPINDLE_REVERSE == 1) {{")
        output.append("                // REV;")
        output.append("                frame_data[3] = 0x11;")
        output.append("            }")
        output.append(f"            if (frame_data[3] != {self.instances_name}_status_last) {{")
        output.append(f"                *data->SIGIN_{utitle}_AT_SPEED = 0;")
        output.append("                frame_len = 4;")
        output.append("            }")
        output.append("        }")
        output.append("    }")
        output.append("    return frame_len;")
        output.append("}")
        output.append("")
        return output

    def func_rx(self):
        address = self.plugin_setup.get("address", self.option_default("address"))
        utitle = self.title.upper()
        num_config_registers = len(self.HYVFD_CONFIG_REGISTER)
        num_status_registers = len(self.HYVFD_STATUS_REGISTER)
        output = []
        output.append(f"void {self.title}_vfd_rx(uint8_t *frame_data, uint8_t frame_len) {{")
        output.append("    uint8_t n = 0;")
        output.append(f"    if (frame_len > 0 && frame_data[0] == {address}) {{")
        output.append("        if (frame_data[1] == 0x01 && frame_data[2] == 0x03) {")
        output.append(f"            for (n = 0; n < {num_config_registers}; n++) {{")
        output.append(f"                if (frame_data[3] == {self.instances_name}_config_register[n].num) {{")
        output.append(f"                    {self.instances_name}_config_register[n].done = 1;")
        output.append(f"                    {self.instances_name}_config_register[n].value = (frame_data[4]<<8) + (frame_data[5] & 0xFF);")
        output.append("                    break;")
        output.append("                }")
        output.append("            }")
        output.append(f"            *data->SIGIN_{utitle}_HYCOMM_OK = 1;")
        output.append("        } else if (frame_data[1] == 0x04 && frame_data[2] == 0x03) {")
        output.append(f"            for (n = 0; n < {num_status_registers}; n++) {{")
        output.append(f"                if (frame_data[3] == {self.instances_name}_status_register[n].num) {{")
        output.append(f"                    {self.instances_name}_status_register[n].value = (frame_data[4]<<8) + (frame_data[5] & 0xFF);")
        vn = 0
        for register, data in self.HYVFD_STATUS_REGISTER.items():
            output.append(f"                    if (n == {vn}) {{")
            output.append(f"                        *data->SIGIN_{utitle}_{data['name'].upper()} = {self.instances_name}_status_register[n].value * {data['scale']};")
            output.append("                    }")
            vn += 1
        output.append("                    break;")
        output.append("                }")
        output.append("            }")
        output.append(f"            if (*data->SIGIN_{utitle}_MAX_FREQ > 0.0) {{")
        output.append(f"                *data->SIGIN_{utitle}_SPEED_FB = *data->SIGIN_{utitle}_FRQ_GET / *data->SIGIN_{utitle}_MAX_FREQ * *data->SIGIN_{utitle}_RATED_MOTOR_REV * {self.HYVFD_CALC_KEYS['speed_fb']['scale']};")
        output.append("            }")
        output.append(f"            *data->SIGIN_{utitle}_SPEED_FB_RPS = *data->SIGIN_{utitle}_SPEED_FB / 60.0;")
        output.append(f"            if (*data->SIGOUT_{utitle}_SPINDLE_AT_SPEED_TOLERANCE == 0.0) {{")
        output.append(f"                *data->SIGOUT_{utitle}_SPINDLE_AT_SPEED_TOLERANCE = 5.0;")
        output.append("            }")
        output.append(f"            float tolerance =  fabs(*data->SIGOUT_{utitle}_SPEED_COMMAND) * *data->SIGOUT_{utitle}_SPINDLE_AT_SPEED_TOLERANCE / 100.0;")
        output.append(f"            float diff =  fabs(*data->SIGIN_{utitle}_SPEED_FB) -  fabs(*data->SIGOUT_{utitle}_SPEED_COMMAND);")
        output.append("            if (diff <= tolerance) {")
        output.append(f"                *data->SIGIN_{utitle}_AT_SPEED = 1;")
        output.append("            } else {")
        output.append(f"                *data->SIGIN_{utitle}_AT_SPEED = 0;")
        output.append("            }")
        output.append(f"            *data->SIGIN_{utitle}_HYCOMM_OK = 1;")
        output.append(f"            if (*data->SIGIN_{utitle}_ERROR_COUNT > 0) {{")
        output.append(f"                *data->SIGIN_{utitle}_ERROR_COUNT -= 1;")
        output.append("            }")
        output.append("        } else if (frame_data[1] == 0x05 && frame_data[2] == 0x02) {")
        output.append(f"            *data->SIGIN_{utitle}_HYCOMM_OK = 1;")
        output.append(f"            {self.instances_name}_speed_last = (frame_data[3]<<8) + (frame_data[4] & 0xFF);")
        output.append("        } else if (frame_data[1] == 0x03 && frame_data[2] == 0x01) {")
        output.append(f"            *data->SIGIN_{utitle}_HYCOMM_OK = 1;")
        output.append("            if (frame_data[3] == 0) {")
        output.append(f"                {self.instances_name}_status_last = 8;")
        output.append("            }")
        output.append("            if (frame_data[3] == 9) {")
        output.append(f"                {self.instances_name}_status_last = 1;")
        output.append("            }")
        output.append("            if (frame_data[3] == 45) {")
        output.append(f"                {self.instances_name}_status_last = 11;")
        output.append("            }")
        output.append("        } else {")
        output.append("            // ERROR")
        output.append(f"            *data->SIGIN_{utitle}_ERROR_COUNT += 1;")
        output.append(f"            *data->SIGIN_{utitle}_HYCOMM_OK = 0;")
        output.append(f"            *data->SIGIN_{utitle}_AT_SPEED = 0;")
        output.append("        }")
        output.append(f"        *data->SIGIN_{utitle}_BASE_FREQ = {self.instances_name}_config_register[0].value * {self.HYVFD_CALC_KEYS['base_freq']['scale']};")
        output.append(f"        *data->SIGIN_{utitle}_MAX_FREQ = {self.instances_name}_config_register[1].value * {self.HYVFD_CALC_KEYS['max_freq']['scale']};")
        output.append(f"        *data->SIGIN_{utitle}_FREQ_LOWER_LIMIT = {self.instances_name}_config_register[2].value * {self.HYVFD_CALC_KEYS['freq_lower_limit']['scale']};")
        output.append(f"        *data->SIGIN_{utitle}_RATED_MOTOR_VOLTAGE = {self.instances_name}_config_register[3].value * {self.HYVFD_CALC_KEYS['rated_motor_voltage']['scale']};")
        output.append(f"        *data->SIGIN_{utitle}_RATED_MOTOR_CURRENT = {self.instances_name}_config_register[4].value * {self.HYVFD_CALC_KEYS['rated_motor_current']['scale']};")
        output.append(f"        *data->SIGIN_{utitle}_RPM_AT_50HZ = {self.instances_name}_config_register[5].value * {self.HYVFD_CALC_KEYS['rpm_at_50hz']['scale']};")
        output.append(f"        *data->SIGIN_{utitle}_RATED_MOTOR_REV = (*data->SIGIN_{utitle}_RPM_AT_50HZ / 50.0) * *data->SIGIN_{utitle}_MAX_FREQ;")
        output.append(f"        *data->SIGIN_{self.title.upper()}_VFD_ERRORS = *data->SIGIN_{utitle}_ERROR_COUNT;")
        output.append("    }")
        output.append("}")
        output.append("")
        return output

    def device_functions(self, bus_master):
        output = []
        output.append(f"// generated by plugin: {self.NAME}")
        output.append("")
        output.append(self.predefines())
        output.append(f"uint8_t {self.title}_vfd_changed() {{")
        output.append(f"    if ({self.instances_name}_register_setup == 1) {{")
        output.append("        return 1;")
        output.append("    }")
        output.append("    return 0;")
        output.append("}")
        output.append("")
        output += self.func_tx()
        output += self.func_rx()
        return "\n".join(output)
