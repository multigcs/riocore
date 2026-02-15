from riocore.checksums import crc16


class hy_vfd:
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
        "speed_command": {"direction": "output", "unit": "RPM", "net": "spindle.0.speed-out-abs", "display": {"section": "vfd", "title": "Speed-Set", "format": "d"}},
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

    def __init__(self, signals, signal_name, config):
        self.signals = signals
        self.signal_name = signal_name
        self.config = config
        for register, data in self.HYVFD_STATUS_REGISTER.items():
            value_name = f"{signal_name}_{data['name']}"
            self.signals[value_name] = {
                "direction": "input",
                "net": data.get("net", ""),
                "unit": data.get("unit", ""),
                "scale": 1.0,
                "format": "7.2f",
                "plugin_setup": config,
                "display": data.get("display", {}),
                "helper": True,
            }
        for name, data in self.HYVFD_CALC_KEYS.items():
            self.HYVFD_DATA[name] = 0
            value_name = f"{signal_name}_{name}"
            self.signals[value_name] = {
                "direction": "input",
                "net": data.get("net", ""),
                "unit": data.get("unit", ""),
                "bool": data.get("bool", False),
                "helper": data.get("helper", True),
                "display": data.get("display", {}),
                "scale": 1.0,
                "format": ".2f",
                "plugin_setup": config,
            }
        for name, data in self.HYVFD_SIGNALS.items():
            value_name = f"{signal_name}_{name}"
            if data.get("bool", False) is True:
                self.signals[value_name] = {
                    "direction": data.get("direction", "output"),
                    "plugin_setup": config,
                    "net": data.get("net", ""),
                    "unit": data.get("unit", ""),
                    "helper": data.get("helper", False),
                    "display": data.get("display", {}),
                    "bool": True,
                }
            else:
                self.signals[value_name] = {
                    "direction": data.get("direction", "output"),
                    "net": data.get("net", ""),
                    "unit": data.get("unit", ""),
                    "scale": 1.0,
                    "format": "7.2f",
                    "plugin_setup": config,
                    "helper": data.get("helper", False),
                    "display": data.get("display", {}),
                    "min": -24000,
                    "max": 24000,
                }

    def int2list(self, value):
        return [(value >> 8) & 0xFF, value & 0xFF]

    def list2int(self, data):
        return (data[0] << 8) + data[1]

    def globals_c(self, instances_name):
        self.instances_name = instances_name
        output = []
        output.append(f"uint8_t {self.instances_name}_{self.signal_name}_register_setup = 1;")
        output.append(f"uint8_t {self.instances_name}_{self.signal_name}_status_read = 0;")
        output.append(f"uint8_t {self.instances_name}_{self.signal_name}_set_speed = 0;")
        output.append(f"uint8_t {self.instances_name}_{self.signal_name}_command = 0;")
        output.append(f"uint8_t {self.instances_name}_{self.signal_name}_status_register_active = 0;")
        output.append("")
        num_config_registers = len(self.HYVFD_CONFIG_REGISTER)
        output.append("typedef struct {;")
        output.append("    float value;")
        output.append("    uint8_t num;")
        output.append("    uint8_t done;")
        output.append("    uint8_t try;")
        output.append(f"}} {self.instances_name}_{self.signal_name}_config_register_t;")
        output.append("")
        output.append(f"{self.instances_name}_{self.signal_name}_config_register_t {self.instances_name}_{self.signal_name}_config_register[{num_config_registers}] = {{")
        for register, data in self.HYVFD_CONFIG_REGISTER.items():
            output.append(f"    {{0.0, {register}, 0, 0}},")
        output.append("};")
        output.append("")
        num_status_registers = len(self.HYVFD_STATUS_REGISTER)
        output.append("typedef struct {;")
        output.append("    float value;")
        output.append("    uint8_t num;")
        output.append("    uint8_t done;")
        output.append("    uint8_t try;")
        output.append(f"}} {self.instances_name}_{self.signal_name}_status_register_t;")
        output.append("")
        output.append(f"{self.instances_name}_{self.signal_name}_status_register_t {self.instances_name}_{self.signal_name}_status_register[{num_status_registers}] = {{")
        for register, data in self.HYVFD_STATUS_REGISTER.items():
            output.append(f"    {{0.0, {register}, 0, 0}},")
        output.append("};")
        output.append(f"uint16_t {self.instances_name}_{self.signal_name}_speed_last = 0xFFFF;")
        output.append(f"int8_t {self.instances_name}_{self.signal_name}_status_last = 0xFF;")
        output.append("")
        return output

    def frameio_rx_c(self):
        address = self.config["address"]
        output = []
        output.append(f"    if (data_addr == {address}) {{")
        output.append("        if (frame_data[1] == 0x01 && frame_data[2] == 0x03) {")
        num_config_registers = len(self.HYVFD_CONFIG_REGISTER)
        output.append(f"            for (n = 0; n < {num_config_registers}; n++) {{")
        output.append(f"                if (frame_data[3] == {self.instances_name}_{self.signal_name}_config_register[n].num) {{")
        output.append(f"                    {self.instances_name}_{self.signal_name}_config_register[n].done = 1;")
        output.append(f"                    {self.instances_name}_{self.signal_name}_config_register[n].value = (frame_data[4]<<8) + (frame_data[5] & 0xFF);")
        output.append("                    break;")
        output.append("                }")
        output.append("            }")
        output.append(f"            value_{self.signal_name}_hycomm_ok = 1;")
        output.append("        } else if (frame_data[1] == 0x04 && frame_data[2] == 0x03) {")
        num_status_registers = len(self.HYVFD_STATUS_REGISTER)
        output.append(f"            for (n = 0; n < {num_status_registers}; n++) {{")
        output.append(f"                if (frame_data[3] == {self.instances_name}_{self.signal_name}_status_register[n].num) {{")
        output.append(f"                    {self.instances_name}_{self.signal_name}_status_register[n].value = (frame_data[4]<<8) + (frame_data[5] & 0xFF);")
        vn = 0
        for register, data in self.HYVFD_STATUS_REGISTER.items():
            output.append(f"                    if (n == {vn}) {{")
            output.append(f"                        value_{self.signal_name}_{data['name']} = {self.instances_name}_{self.signal_name}_status_register[n].value * {data['scale']};")
            output.append("                    }")
            vn += 1
        output.append("                    break;")
        output.append("                }")
        output.append("            }")
        output.append(f"            if (value_{self.signal_name}_max_freq > 0.0) {{")
        output.append(f"                value_{self.signal_name}_speed_fb = value_{self.signal_name}_frq_get / value_{self.signal_name}_max_freq * value_{self.signal_name}_rated_motor_rev * {self.HYVFD_CALC_KEYS['speed_fb']['scale']};")
        output.append("            }")
        output.append(f"            value_{self.signal_name}_speed_fb_rps = value_{self.signal_name}_speed_fb / 60.0;")
        output.append(f"            if (value_{self.signal_name}_spindle_at_speed_tolerance == 0.0) {{")
        output.append(f"                value_{self.signal_name}_spindle_at_speed_tolerance = 5.0;")
        output.append("            }")
        output.append(f"            float tolerance =  fabs(value_{self.signal_name}_speed_command) * value_{self.signal_name}_spindle_at_speed_tolerance / 100.0;")
        output.append(f"            float diff =  fabs(value_{self.signal_name}_speed_fb) -  fabs(value_{self.signal_name}_speed_command);")
        output.append("            if (diff <= tolerance) {")
        output.append(f"                value_{self.signal_name}_at_speed = 1;")
        output.append("            } else {")
        output.append(f"                value_{self.signal_name}_at_speed = 0;")
        output.append("            }")
        output.append(f"            value_{self.signal_name}_hycomm_ok = 1;")
        output.append(f"            if (value_{self.signal_name}_error_count > 0) {{")
        output.append(f"                value_{self.signal_name}_error_count -= 1;")
        output.append("            }")
        output.append("        } else if (frame_data[1] == 0x05 && frame_data[2] == 0x02) {")
        output.append(f"            value_{self.signal_name}_hycomm_ok = 1;")
        output.append(f"            {self.instances_name}_{self.signal_name}_speed_last = (frame_data[3]<<8) + (frame_data[4] & 0xFF);")
        output.append("        } else if (frame_data[1] == 0x03 && frame_data[2] == 0x01) {")
        output.append(f"            value_{self.signal_name}_hycomm_ok = 1;")
        output.append("            if (frame_data[3] == 0) {")
        output.append(f"                {self.instances_name}_{self.signal_name}_status_last = 8;")
        output.append("            }")
        output.append("            if (frame_data[3] == 9) {")
        output.append(f"                {self.instances_name}_{self.signal_name}_status_last = 1;")
        output.append("            }")
        output.append("            if (frame_data[3] == 45) {")
        output.append(f"                {self.instances_name}_{self.signal_name}_status_last = 11;")
        output.append("            }")
        output.append("        } else {")
        output.append("            // ERROR")
        output.append(f"            value_{self.signal_name}_error_count += 1;")
        output.append(f"            value_{self.signal_name}_hycomm_ok = 0;")
        output.append(f"            value_{self.signal_name}_at_speed = 0;")
        output.append("        }")
        output.append(f"        value_{self.signal_name}_base_freq = {self.instances_name}_{self.signal_name}_config_register[0].value * {self.HYVFD_CALC_KEYS['base_freq']['scale']};")
        output.append(f"        value_{self.signal_name}_max_freq = {self.instances_name}_{self.signal_name}_config_register[1].value * {self.HYVFD_CALC_KEYS['max_freq']['scale']};")
        output.append(f"        value_{self.signal_name}_freq_lower_limit = {self.instances_name}_{self.signal_name}_config_register[2].value * {self.HYVFD_CALC_KEYS['freq_lower_limit']['scale']};")
        output.append(f"        value_{self.signal_name}_rated_motor_voltage = {self.instances_name}_{self.signal_name}_config_register[3].value * {self.HYVFD_CALC_KEYS['rated_motor_voltage']['scale']};")
        output.append(f"        value_{self.signal_name}_rated_motor_current = {self.instances_name}_{self.signal_name}_config_register[4].value * {self.HYVFD_CALC_KEYS['rated_motor_current']['scale']};")
        output.append(f"        value_{self.signal_name}_rpm_at_50hz = {self.instances_name}_{self.signal_name}_config_register[5].value * {self.HYVFD_CALC_KEYS['rpm_at_50hz']['scale']};")
        output.append(f"        value_{self.signal_name}_rated_motor_rev = (value_{self.signal_name}_rpm_at_50hz / 50.0) * value_{self.signal_name}_max_freq;")
        output.append("    }")
        output.append("    break;")
        output.append("")
        return output

    def frameio_tx_c(self):
        address = self.config["address"]
        output = []
        output.append("uint8_t n = 0;")
        output.append("static uint8_t init_timer = 0;")
        output.append("")
        output.append("")
        output.append("if (frame_timeout == 1) {")
        output.append(f"    value_{self.signal_name}_error_count += 1;")
        output.append(f"    value_{self.signal_name}_hycomm_ok = 0;")
        output.append(f"    value_{self.signal_name}_at_speed = 0;")
        output.append("}")
        output.append("")
        output.append("if (*data->sys_enable == 0 && init_timer++ > 10) {")
        output.append("    init_timer = 0;")
        output.append(f"    {self.instances_name}_{self.signal_name}_register_setup = 1;")
        output.append("    for (n = 0; n < 6; n++) {")
        output.append(f"        {self.instances_name}_{self.signal_name}_config_register[n].try = 0;")
        output.append("    }")
        output.append("}")
        output.append(f"if ({self.instances_name}_{self.signal_name}_register_setup == 1) {{")
        output.append(f"    {self.instances_name}_{self.signal_name}_register_setup = 0;")
        num_config_registers = len(self.HYVFD_CONFIG_REGISTER)
        output.append(f"    for (n = 0; n < {num_config_registers}; n++) {{")
        output.append(f"        if ({self.instances_name}_{self.signal_name}_config_register[n].done == 0 && {self.instances_name}_{self.signal_name}_config_register[n].try < 50) {{")
        output.append(f"            {self.instances_name}_{self.signal_name}_config_register[n].try += 1;")
        output.append(f"            {self.instances_name}_{self.signal_name}_register_setup = 1;")
        output.append(f"            frame_data[0] = {address};")
        output.append("            frame_data[1] = 0x01;")
        output.append("            frame_data[2] = 0x03;")
        output.append(f"            frame_data[3] = {self.instances_name}_{self.signal_name}_config_register[n].num;")
        output.append("            frame_data[4] = 0x00;")
        output.append("            frame_data[5] = 0x00;")
        output.append("            frame_len = 6;")
        output.append("            break;")
        output.append("        }")
        output.append("    }")
        output.append("} else {")
        output.append(f"    if ({self.instances_name}_{self.signal_name}_command < 2) {{")
        output.append(f"        {self.instances_name}_{self.signal_name}_command += 1;")
        output.append("    } else {")
        output.append(f"        {self.instances_name}_{self.signal_name}_command = 0;")
        output.append("    }")
        output.append(f"    if ({self.instances_name}_{self.signal_name}_command == 0) {{")
        output.append("        // do status")
        num_config_registers = len(self.HYVFD_STATUS_REGISTER)
        output.append(f"        if ({self.instances_name}_{self.signal_name}_status_register_active < {num_config_registers - 2}) {{")
        output.append(f"            {self.instances_name}_{self.signal_name}_status_register_active += 1;")
        output.append("        } else {")
        output.append(f"            {self.instances_name}_{self.signal_name}_status_register_active = 0;")
        output.append("        }")
        output.append(f"        frame_data[0] = {address};")
        output.append("        frame_data[1] = 0x04;")
        output.append("        frame_data[2] = 0x03;")
        output.append(f"        frame_data[3] = {self.instances_name}_{self.signal_name}_status_register[{self.instances_name}_{self.signal_name}_status_register_active].num;")
        output.append("        frame_data[4] = 0x00;")
        output.append("        frame_data[5] = 0x00;")
        output.append("        frame_len = 6;")
        output.append(f"    }} else if ({self.instances_name}_{self.signal_name}_command == 1) {{")
        output.append("        // set speed")
        output.append("        float freq_comp = 0;")
        output.append("        float hz_per_rpm = 0;")
        output.append(f"        if (value_{self.signal_name}_rated_motor_rev > 0.0) {{")
        output.append(f"            hz_per_rpm = value_{self.signal_name}_max_freq / value_{self.signal_name}_rated_motor_rev;")
        output.append("        }")
        output.append(f"        float value =  fabs((value_{self.signal_name}_speed_command + freq_comp) * hz_per_rpm);")
        output.append(f"        if (value > value_{self.signal_name}_max_freq) {{")
        output.append(f"            value = value_{self.signal_name}_max_freq;")
        output.append("        }")
        output.append(f"        if (value < value_{self.signal_name}_freq_lower_limit) {{")
        output.append(f"            value = value_{self.signal_name}_freq_lower_limit;")
        output.append("        }")
        output.append("        uint16_t value_int = value * 100.0;")
        output.append(f"        if (value_int != {self.instances_name}_{self.signal_name}_speed_last) {{")
        output.append(f"            value_{self.signal_name}_at_speed = 0;")
        output.append(f"            frame_data[0] = {address};")
        output.append("            frame_data[1] = 0x05;")
        output.append("            frame_data[2] = 0x02;")
        output.append("            frame_data[3] = value_int>>8 & 0xFF;")
        output.append("            frame_data[4] = value_int & 0xFF;")
        output.append("            frame_len = 5;")
        output.append("        }")
        output.append(f"    }} else if ({self.instances_name}_{self.signal_name}_command == 2) {{")
        output.append(f"        frame_data[0] = {address};")
        output.append("        frame_data[1] = 0x03;")
        output.append("        frame_data[2] = 0x01;")
        output.append(f"        if (value_{self.signal_name}_spindle_on == 0) {{")
        output.append("            // STOP;")
        output.append("            frame_data[3] = 0x08;")
        output.append(f"        }} else if (value_{self.signal_name}_spindle_forward == 1) {{")
        output.append("            // FWD;")
        output.append("            frame_data[3] = 0x01;")
        output.append(f"        }} else if (value_{self.signal_name}_spindle_reverse == 1) {{")
        output.append("            // REV;")
        output.append("            frame_data[3] = 0x11;")
        output.append("        }")
        output.append(f"        if (frame_data[3] != {self.instances_name}_{self.signal_name}_status_last) {{")
        output.append(f"            value_{self.signal_name}_at_speed = 0;")
        output.append("            frame_len = 4;")
        output.append("        }")
        output.append("    }")
        output.append("}")
        output.append("")
        return output

    def on_error(self):
        cmds = []
        address = self.config["address"]
        for cmd in self.HYVFD_ON_ERROR_CMDS:
            frame = [address, *cmd]
            csum = crc16()
            csum.update(frame)
            frame += csum.intdigest()
            cmds.append(frame)
        return cmds
