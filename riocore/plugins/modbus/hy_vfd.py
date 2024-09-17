from riocore.checksums import crc16


class hy_vfd:
    HYVFD_MAX_TRYS = 100
    HYVFD_ON_ERROR_CMDS = [
        [0x03, 0x01, 0x8],  # stop spindle on error
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
            "display": {"section": "status", "title": "RPM", "type": "meter", "min": 0, "max": 24000, "size": 250, "region": [[0, 6000, "gray"], [6000, 20000, "green"], [20000, 24000, "red"]]},
        },
        "speed_fb_rps": {"scale": 1.0, "unit": "RPS"},
        "at_speed": {"scale": 1.0, "bool": True, "helper": False, "display": {"section": "status", "title": "AT-Speed"}},
        "error_count": {"scale": 1.0, "display": {"section": "vfd", "title": "Errors", "format": "d"}},
        "hycomm_ok": {"scale": 1.0, "bool": True},
    }
    HYVFD_SIGNALS = {
        "speed_command": {"direction": "output", "unit": "RPM", "net": "spindle.0.speed-out-abs", "display": {"section": "vfd", "title": "Speed-Set", "format": "d"}},
        "spindle_at_speed_tolerance": {"direction": "output", "unit": "", "net": "", "helper": True},
        "spindle_forward": {"direction": "output", "bool": True, "net": "spindle0_forward spindle.0.forward", "display": {"type": "none"}},
        "spindle_reverse": {"direction": "output", "bool": True, "net": "spindle0_reverse spindle.0.reverse", "display": {"type": "none"}},
        "spindle_on": {"direction": "output", "bool": True, "net": "spindle0_on spindle.0.on", "display": {"type": "none"}},
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
                "plugin_setup": {},
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
                "plugin_setup": {},
            }
        for name, data in self.HYVFD_SIGNALS.items():
            value_name = f"{signal_name}_{name}"
            if data.get("bool", False) is True:
                self.signals[value_name] = {
                    "direction": "output",
                    "net": data.get("net", ""),
                    "unit": data.get("unit", ""),
                    "helper": data.get("helper", False),
                    "display": data.get("display", {}),
                    "bool": True,
                }
            else:
                self.signals[value_name] = {
                    "direction": "output",
                    "net": data.get("net", ""),
                    "unit": data.get("unit", ""),
                    "scale": 1.0,
                    "format": "7.2f",
                    "plugin_setup": {},
                    "helper": data.get("helper", False),
                    "display": data.get("display", {}),
                    "min": -24000,
                    "max": 24000,
                }

    def int2list(self, value):
        return [(value >> 8) & 0xFF, value & 0xFF]

    def list2int(self, data):
        return (data[0] << 8) + data[1]

    def frameio_rx(self, frame_new, frame_id, frame_len, frame_data):
        config = self.config
        if frame_new:
            # print(f"hy rx frame  {frame_id} {frame_len}: {frame_data}")
            if frame_len > 4:
                frame_data[0]
                frame_data[1]
                frame_data[2]
                csum = crc16()
                csum.update(frame_data[:-2])
                csum_calc = csum.intdigest()
                if csum_calc != frame_data[-2:]:
                    print(f"ERROR: modbus CSUM failed {csum_calc} != {frame_data[-2:]}")
                else:
                    if frame_data[0] == config["address"]:
                        if frame_data[1] == 0x01 and frame_data[2] == 0x03:
                            register = frame_data[3]
                            value = self.list2int(frame_data[4:-2])
                            self.HYVFD_CONFIG_REGISTER[register]["value"] = value
                            self.HYVFD_CONFIG_REGISTER[register]["done"] = True
                        elif frame_data[1] == 0x04 and frame_data[2] == 0x03:
                            status_register = frame_data[3]
                            status_name = self.HYVFD_STATUS_REGISTER[status_register]["name"]
                            status_scale = self.HYVFD_STATUS_REGISTER[status_register]["scale"]
                            value = self.list2int(frame_data[4:-2])
                            self.HYVFD_STATUS_REGISTER[status_register]["done"] = True
                            if status_register == 1:
                                self.HYVFD_DATA[status_name] = value * status_scale
                                self.HYVFD_DATA["speed_fb"] = self.HYVFD_DATA["frq_get"] / self.HYVFD_DATA["max_freq"] * self.HYVFD_DATA["rated_motor_rev"] * self.HYVFD_CALC_KEYS["speed_fb"]["scale"]
                                self.HYVFD_DATA["speed_fb_rps"] = self.HYVFD_DATA["speed_fb"] / 60.0
                                set_speed = self.signals[f"{self.signal_name}_speed_command"]["value"]
                                tolerance = set_speed * self.signals[f"{self.signal_name}_spindle_at_speed_tolerance"]["value"]
                                diff = self.HYVFD_DATA["speed_fb"] - set_speed
                                if diff <= tolerance:
                                    self.HYVFD_DATA["at_speed"] = 1
                                else:
                                    self.HYVFD_DATA["at_speed"] = 0
                            else:
                                self.HYVFD_DATA[status_name] = value * status_scale
                            self.HYVFD_DATA["hycomm_ok"] = 1
                        elif frame_data[1] == 0x05 and frame_data[2] == 0x02:
                            pass
                            self.HYVFD_DATA["hycomm_ok"] = 1
                        elif frame_data[1] == 0x03 and frame_data[2] == 0x01:
                            pass
                            self.HYVFD_DATA["hycomm_ok"] = 1
                        else:
                            self.HYVFD_DATA["error_count"] += 1
                            self.HYVFD_DATA["hycomm_ok"] = 0
                    for name, value in self.HYVFD_DATA.items():
                        value_name = f"{self.signal_name}_{name}"
                        if value_name in self.signals:
                            self.signals[value_name]["value"] = value

    def frameio_tx(self, frame_ack, frame_timeout):
        cmd = []
        config = self.config
        config["direction"]
        address = config["address"]
        config["type"]
        self.signal_address = address
        if self.HYVFD_CONFIG_REGISTER_SETUP:
            self.HYVFD_CONFIG_REGISTER_SETUP = False
            for register, reg_data in self.HYVFD_CONFIG_REGISTER.items():
                if not reg_data["done"] and reg_data["try"] < self.HYVFD_MAX_TRYS:
                    self.HYVFD_CONFIG_REGISTER_SETUP = True
                    cmd = [address, 0x01, 0x03, register, 0x00, 0x00]
                    reg_data["try"] += 1
                    break
        else:
            if self.HYVFD_COMMAND < 2:
                self.HYVFD_COMMAND += 1
            else:
                self.HYVFD_COMMAND = 0
            if self.HYVFD_COMMAND == 0 or self.HYVFD_STATUS_READ is False:
                # calculate setup values
                self.HYVFD_DATA["max_freq"] = self.HYVFD_CONFIG_REGISTER[5]["value"] * self.HYVFD_CALC_KEYS["max_freq"]["scale"]
                self.HYVFD_DATA["base_freq"] = self.HYVFD_CONFIG_REGISTER[4]["value"] * self.HYVFD_CALC_KEYS["base_freq"]["scale"]
                self.HYVFD_DATA["freq_lower_limit"] = self.HYVFD_CONFIG_REGISTER[11]["value"] * self.HYVFD_CALC_KEYS["freq_lower_limit"]["scale"]
                self.HYVFD_DATA["rated_motor_voltage"] = self.HYVFD_CONFIG_REGISTER[141]["value"] * self.HYVFD_CALC_KEYS["rated_motor_voltage"]["scale"]
                self.HYVFD_DATA["rated_motor_current"] = self.HYVFD_CONFIG_REGISTER[142]["value"] * self.HYVFD_CALC_KEYS["rated_motor_current"]["scale"]
                self.HYVFD_DATA["rpm_at_50hz"] = self.HYVFD_CONFIG_REGISTER[144]["value"] * self.HYVFD_CALC_KEYS["rpm_at_50hz"]["scale"]
                self.HYVFD_DATA["rated_motor_rev"] = (self.HYVFD_DATA["rpm_at_50hz"] / 50.0) * self.HYVFD_DATA["max_freq"]
                # get status data
                if self.HYVFD_STATUS_REGISTER_ACTIVE < len(self.HYVFD_STATUS_REGISTER) - 1:
                    self.HYVFD_STATUS_REGISTER_ACTIVE += 1
                else:
                    self.HYVFD_STATUS_REGISTER_ACTIVE = 0
                    self.HYVFD_STATUS_READ = True
                status_register = list(self.HYVFD_STATUS_REGISTER)[self.HYVFD_STATUS_REGISTER_ACTIVE]
                status_name = self.HYVFD_STATUS_REGISTER[status_register]["name"]
                if status_name not in self.HYVFD_DATA:
                    self.HYVFD_DATA[status_name] = 0.0
                cmd = [address, 0x04, 0x03, status_register, 0x00, 0x00]
            elif self.HYVFD_COMMAND == 1:
                set_speed = self.signals[f"{self.signal_name}_speed_command"]["value"]
                freq_comp = 0
                hz_per_rpm = self.HYVFD_DATA["max_freq"] / self.HYVFD_DATA["rated_motor_rev"]
                value = abs((set_speed + freq_comp) * hz_per_rpm)
                if value > self.HYVFD_DATA["max_freq"]:
                    value = self.HYVFD_DATA["max_freq"]
                if value < self.HYVFD_DATA["freq_lower_limit"]:
                    value = self.HYVFD_DATA["freq_lower_limit"]
                cmd = [address, 0x05, 0x02] + self.int2list(int(value * 100))
            elif self.HYVFD_COMMAND == 2:
                set_speed = self.signals[f"{self.signal_name}_speed_command"]["value"]
                if set_speed > 0.0:
                    # FWD
                    cmd = [address, 0x03, 0x01, 0x1]
                elif set_speed < 0.0:
                    # REV
                    cmd = [address, 0x03, 0x01, 0x11]
                else:
                    # STOP
                    cmd = [address, 0x03, 0x01, 0x8]
        return cmd

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
        output.append(
            f"            value_{self.signal_name}_speed_fb = value_{self.signal_name}_frq_get / value_{self.signal_name}_max_freq * value_{self.signal_name}_rated_motor_rev * {self.HYVFD_CALC_KEYS['speed_fb']['scale']};"
        )
        output.append(f"            value_{self.signal_name}_speed_fb_rps = value_{self.signal_name}_speed_fb / 60.0;")
        output.append(f"            float tolerance = value_{self.signal_name}_speed_command * value_{self.signal_name}_spindle_at_speed_tolerance;")
        output.append(f"            float diff = abs(value_{self.signal_name}_speed_fb - value_{self.signal_name}_speed_command);")
        output.append("            if (diff <= tolerance) {")
        output.append(f"                value_{self.signal_name}_at_speed = 1;")
        output.append("            } else {")
        output.append(f"                value_{self.signal_name}_at_speed = 0;")
        output.append("            }")
        output.append(f"            value_{self.signal_name}_hycomm_ok = 1;")
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
        output.append("        }")
        output.append(f"        value_{self.signal_name}_base_freq = {self.instances_name}_{self.signal_name}_config_register[0].value * {self.HYVFD_CALC_KEYS['base_freq']['scale']};")
        output.append(f"        value_{self.signal_name}_max_freq = {self.instances_name}_{self.signal_name}_config_register[1].value * {self.HYVFD_CALC_KEYS['max_freq']['scale']};")
        output.append(f"        value_{self.signal_name}_freq_lower_limit = {self.instances_name}_{self.signal_name}_config_register[2].value * {self.HYVFD_CALC_KEYS['freq_lower_limit']['scale']};")
        output.append(
            f"        value_{self.signal_name}_rated_motor_voltage = {self.instances_name}_{self.signal_name}_config_register[3].value * {self.HYVFD_CALC_KEYS['rated_motor_voltage']['scale']};"
        )
        output.append(
            f"        value_{self.signal_name}_rated_motor_current = {self.instances_name}_{self.signal_name}_config_register[4].value * {self.HYVFD_CALC_KEYS['rated_motor_current']['scale']};"
        )
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
        output.append("")
        output.append(f"if ({self.instances_name}_{self.signal_name}_register_setup == 1) {{")
        output.append(f"    {self.instances_name}_{self.signal_name}_register_setup = 0;")
        num_config_registers = len(self.HYVFD_CONFIG_REGISTER)
        output.append(f"    for (n = 0; n < {num_config_registers}; n++) {{")
        output.append(f"        if ({self.instances_name}_{self.signal_name}_config_register[n].done == 0 && {self.instances_name}_{self.signal_name}_config_register[n].try < 5) {{")
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
        output.append(f"    if ({self.instances_name}_{self.signal_name}_status_register_active < {num_config_registers - 2}) {{")
        output.append(f"        {self.instances_name}_{self.signal_name}_status_register_active += 1;")
        output.append("    } else {")
        output.append(f"        {self.instances_name}_{self.signal_name}_status_register_active = 0;")
        output.append("    }")
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
        output.append(f"        for (n = 0; n < {num_config_registers}; n++) {{")
        output.append(f"            if ({self.instances_name}_{self.signal_name}_status_register_active == n) {{")
        output.append(f"                frame_data[0] = {address};")
        output.append("                frame_data[1] = 0x04;")
        output.append("                frame_data[2] = 0x03;")
        output.append(f"                frame_data[3] = {self.instances_name}_{self.signal_name}_status_register[n].num;")
        output.append("                frame_data[4] = 0x00;")
        output.append("                frame_data[5] = 0x00;")
        output.append("                frame_len = 6;")
        output.append("                break;")
        output.append("            }")
        output.append("        }")
        output.append(f"    }} else if ({self.instances_name}_{self.signal_name}_command == 1) {{")
        output.append("        // set speed")
        output.append("        float freq_comp = 0;")
        output.append(f"        float hz_per_rpm = value_{self.signal_name}_max_freq / value_{self.signal_name}_rated_motor_rev;")
        output.append(f"        float value = abs((value_{self.signal_name}_speed_command + freq_comp) * hz_per_rpm);")
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
            frame = [address] + cmd
            csum = crc16()
            csum.update(frame)
            frame += csum.intdigest()
            cmds.append(frame)
        return cmds
