import os
from struct import *

from riocore.checksums import crc8, crc16
from riocore.plugins import PluginBase


class modbus_hy_vfd:
    HYVFD_CALC_KEYS = {
        "max_freq": {"scale": 0.001, "unit": "Hz"},
        "base_freq": {"scale": 0.001, "unit": "Hz"},
        "freq_lower_limit": {"scale": 0.001, "unit": "Hz"},
        "rated_motor_voltage": {"scale": 0.1, "unit": "V"},
        "rated_motor_current": {"scale": 0.1, "unit": "A"},
        "rpm_at_50hz": {"scale": 10.0, "unit": "RPM"},
        "rated_motor_rev": {"scale": 1.0, "unit": "RPM"},
        "speed_fb": {"scale": 1.0, "unit": "RPM"},
        "speed_fb_rps": {"scale": 1.0, "unit": "RPS"},
        "at_speed": {"scale": 1.0},
    }

    HYVFD_OUTPUTS = {
        "speed": {},
    }

    HYVFD_REGISTER_SETUP = True
    HYVFD_STATUS_READ = False
    HYVFD_DATA = {}
    HYVFD_REGISTER = {
        4: {"done": False, "value": 0, "try": 0, "name": ""},
        5: {"done": False, "value": 0, "try": 0, "name": ""},
        11: {"done": False, "value": 0, "try": 0, "name": ""},
        141: {"done": False, "value": 0, "try": 0, "name": ""},
        142: {"done": False, "value": 0, "try": 0, "name": ""},
        # 143: {"done": False, "value": 0, "try": 0, "name": ""},
        144: {"done": False, "value": 0, "try": 0, "name": ""},
    }
    HYVFD_SET_SPEED = 0
    HYVFD_COMMAND = 0
    HYVFD_STATUS_REGISTER_ACTIVE = 0
    HYVFD_STATUS_REGISTER = {
        0: {"done": False, "value": 0, "name": "frq_set", "scale": 0.001, "unit": "Hz"},
        1: {"done": False, "value": 0, "name": "frq_get", "scale": 0.001, "unit": "Hz"},
        2: {"done": False, "value": 0, "name": "ampere", "scale": 0.01, "unit": "A"},
        3: {"done": False, "value": 0, "name": "rpm", "scale": 1.0, "unit": "RPM"},
        4: {"done": False, "value": 0, "name": "dc_volt", "scale": 0.1, "unit": "V"},
        5: {"done": False, "value": 0, "name": "ac_volt", "scale": 0.1, "unit": "V"},
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
                "unit": data.get("unit", ""),
                "scale": 1.0,
                "format": "7.2f",
                "plugin_setup": {},
            }
        for name, data in self.HYVFD_CALC_KEYS.items():
            value_name = f"{signal_name}_{name}"
            self.signals[value_name] = {
                "direction": "input",
                "unit": data.get("unit", ""),
                "scale": 1.0,
                "format": ".2f",
                "plugin_setup": {},
            }
        for name, data in self.HYVFD_OUTPUTS.items():
            value_name = f"{signal_name}_{name}"
            self.signals[value_name] = {
                "direction": "output",
                "unit": data.get("unit", ""),
                "scale": 1.0,
                "format": "7.2f",
                "plugin_setup": {},
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
            # print(f"rx frame {self.signal_active} {frame_id} {frame_len}: {frame_data}")
            if frame_len > 4:
                address = frame_data[0]
                ctype = frame_data[1]
                data_len = frame_data[2]
                csum = crc16()
                cmd = []
                csum.update(frame_data[:-2])
                csum_calc = csum.intdigest()
                if csum_calc != frame_data[-2:]:
                    print(f"ERROR: modbus CSUM failed {csum_calc} != {frame_data[-2:]}")
                else:
                    if frame_data[0] == config["address"]:
                        if frame_data[1] == 0x01 and frame_data[2] == 0x03:
                            register = frame_data[3]
                            value = self.list2int(frame_data[4:-2])
                            self.HYVFD_REGISTER[register]["value"] = value
                            self.HYVFD_REGISTER[register]["done"] = True

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
                                set_speed = self.signals[f"{self.signal_name}_speed"]["value"]

                                tolerance = 10
                                diff = self.HYVFD_DATA["speed_fb"] - set_speed
                                if diff < tolerance:
                                    self.HYVFD_DATA["at_speed"] = 1
                                else:
                                    self.HYVFD_DATA["at_speed"] = 0
                            else:
                                self.HYVFD_DATA[status_name] = value * status_scale

                    for name, value in self.HYVFD_DATA.items():
                        value_name = f"{self.signal_name}_{name}"
                        if value_name in self.signals:
                            self.signals[value_name]["value"] = value

    def frameio_tx(self, frame_ack, frame_timeout):
        cmd = []
        sn = 0
        config = self.config

        direction = config["direction"]
        address = config["address"]
        ctype = config["type"]
        signal_name = self.signal_name
        self.signal_address = address

        if self.HYVFD_REGISTER_SETUP:
            self.HYVFD_REGISTER_SETUP = False
            for register, reg_data in self.HYVFD_REGISTER.items():
                if not reg_data["done"] and reg_data["try"] < 5:
                    self.HYVFD_REGISTER_SETUP = True
                    cmd = [address, 0x01, 0x03, register, 0x00, 0x00]
                    reg_data["try"] += 1
                    break
        else:
            if self.HYVFD_COMMAND < 2:
                self.HYVFD_COMMAND += 1
            else:
                self.HYVFD_COMMAND = 0

            if self.HYVFD_COMMAND == 0 or self.HYVFD_STATUS_READ == False:
                # calculate setup values
                self.HYVFD_DATA["max_freq"] = self.HYVFD_REGISTER[5]["value"] * self.HYVFD_CALC_KEYS["max_freq"]["scale"]
                self.HYVFD_DATA["base_freq"] = self.HYVFD_REGISTER[4]["value"] * self.HYVFD_CALC_KEYS["base_freq"]["scale"]
                self.HYVFD_DATA["freq_lower_limit"] = self.HYVFD_REGISTER[11]["value"] * self.HYVFD_CALC_KEYS["freq_lower_limit"]["scale"]
                self.HYVFD_DATA["rated_motor_voltage"] = self.HYVFD_REGISTER[141]["value"] * self.HYVFD_CALC_KEYS["rated_motor_voltage"]["scale"]
                self.HYVFD_DATA["rated_motor_current"] = self.HYVFD_REGISTER[142]["value"] * self.HYVFD_CALC_KEYS["rated_motor_current"]["scale"]
                self.HYVFD_DATA["rpm_at_50hz"] = self.HYVFD_REGISTER[144]["value"] * self.HYVFD_CALC_KEYS["rpm_at_50hz"]["scale"]
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
                set_speed = self.signals[f"{self.signal_name}_speed"]["value"]
                freq_comp = 0
                hz_per_rpm = self.HYVFD_DATA["max_freq"] / self.HYVFD_DATA["rated_motor_rev"]
                value = abs((set_speed + freq_comp) * hz_per_rpm)
                if value > self.HYVFD_DATA["max_freq"]:
                    value = self.HYVFD_DATA["max_freq"]
                if value < self.HYVFD_DATA["freq_lower_limit"]:
                    value = self.HYVFD_DATA["freq_lower_limit"]
                cmd = [address, 0x05, 0x02] + self.int2list(int(value * 1000))

            elif self.HYVFD_COMMAND == 2:
                set_speed = self.signals[f"{self.signal_name}_speed"]["value"]
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


class Plugin(PluginBase):
    def setup(self):
        self.NAME = "modbus"
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
        self.TIMEOUT = 500.0
        self.INFO = "generic modbus plugin"
        self.DESCRIPTION = ""

        self.rx_buffersize = 128
        self.tx_buffersize = 128

        self.OPTIONS["rx_buffersize"]["default"] = self.rx_buffersize
        self.OPTIONS["tx_buffersize"]["default"] = self.tx_buffersize

        rx_buffersize = self.plugin_setup.get("rx_buffersize", self.OPTIONS["rx_buffersize"]["default"])
        tx_buffersize = self.plugin_setup.get("tx_buffersize", self.OPTIONS["tx_buffersize"]["default"])

        if rx_buffersize < self.rx_buffersize:
            print(f"ERROR: {self.NAME}: rx_buffersize too small: {rx_buffersize} < {self.rx_buffersize}")
            exit(1)
        if tx_buffersize < self.tx_buffersize:
            print(f"ERROR: {self.NAME}: tx_buffersize too small: {tx_buffersize} < {self.tx_buffersize}")
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

            if ctype == 101:
                config["instance"] = modbus_hy_vfd(self.SIGNALS, signal_name, config)

            else:
                is_bool = False
                if ctype in {5, 15}:
                    is_bool = True

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
                        }
                        if config["direction"] == "input":
                            self.SIGNALS[f"{value_name}_valid"] = {
                                "direction": "input",
                                "bool": True,
                                "validation": True,
                                "helper": True,
                            }
                            self.SIGNALS[f"{value_name}_errors"] = {
                                "direction": "input",
                                "validation_counter": True,
                                "format": "03d",
                                "helper": True,
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
                    }
                    if config["direction"] == "input":
                        self.SIGNALS[f"{signal_name}_valid"] = {
                            "direction": "input",
                            "bool": True,
                            "validation": True,
                            "helper": True,
                        }
                        self.SIGNALS[f"{signal_name}_errors"] = {
                            "direction": "input",
                            "validation_counter": True,
                            "format": "03d",
                            "helper": True,
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

        # add signals for the documentation if nothing is configured
        if not self.SIGNALS:
            self.SIGNALS = {
                "temperature": {"direction": "input", "unit": "°C", "scale": 0.1, "format": "0.1f"},
            }

        self.signal_active = 0
        self.signal_values = 0
        self.signal_name = None

    def gateware_instances(self):
        instances = self.gateware_instances_base()

        instance = instances[self.instances_name]
        instance_predefines = instance["predefines"]
        instance_parameter = instance["parameter"]
        instance_arguments = instance["arguments"]

        baud = int(self.plugin_setup.get("baud", self.OPTIONS["baud"]["default"]))
        instance_parameter["RX_BUFFERSIZE"] = self.plugin_setup.get("rx_buffersize", self.OPTIONS["rx_buffersize"]["default"])
        instance_parameter["TX_BUFFERSIZE"] = self.plugin_setup.get("tx_buffersize", self.OPTIONS["tx_buffersize"]["default"])
        instance_parameter["ClkFrequency"] = self.system_setup["speed"]
        instance_parameter["Baud"] = baud

        return instances

    def int2list(self, value):
        return [(value >> 8) & 0xFF, value & 0xFF]

    def list2int(self, data):
        return (data[0] << 8) + data[1]

    def frameio_rx(self, frame_new, frame_id, frame_len, frame_data):
        signal_name = list(self.plugin_setup["config"])[self.signal_active]
        config = self.plugin_setup["config"][signal_name]
        if config["type"] == 101:
            config["instance"].frameio_rx(frame_new, frame_id, frame_len, frame_data)

        elif frame_new:
            # print(f"rx frame {self.signal_active} {frame_id} {frame_len}: {frame_data}")
            if frame_len > 4:
                address = frame_data[0]
                ctype = frame_data[1]
                data_len = frame_data[2]
                csum = crc16()
                cmd = []
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
                                    start_pos = 3 + vn * 2
                                    value_list = frame_data[start_pos : start_pos + 2]

                                    if value_list and len(value_list) == 2:
                                        vscale = self.SIGNALS[value_name]["scale"]
                                        direction = self.SIGNALS[value_name]["direction"]
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
                                self.SIGNALS[self.signal_name]["value"] = self.list2int(frame_data[3:-2])
                                if vscale:
                                    self.SIGNALS[self.signal_name]["value"] *= vscale
                                if direction == "input":
                                    self.SIGNALS[f"{self.signal_name}_valid"]["value"] = 1

    def frameio_tx(self, frame_ack, frame_timeout):
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
        else:
            cmd = []
            direction = config["direction"]
            address = config["address"]
            ctype = config["type"]
            self.signal_name = signal_name
            self.signal_address = address

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
                cmd = [address, ctype] + register + n_values

        csum = crc16()
        csum.update(cmd)
        csum_calc = csum.intdigest()
        frame_data = cmd + csum_calc

        # print(f"tx frame -- {len(frame_data)}: {frame_data}")
        return frame_data

    def globals_c(self):
        return f"""
        uint8_t {self.instances_name}_signal_active = 0;
        """

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
            self.signal_values = signal_config.get("values", 1)
            register = self.int2list(signal_config["register"])
            n_values = self.int2list(self.signal_values)
            self.signal_name = signal_name
            self.signal_address = address
            if direction == "input":
                output.append(f"                case {sn}: {{")
                if self.signal_values > 1:
                    output.append(f"                    // get {self.signal_values} 16bit values ({signal_name})")
                    output.append("                    data_len = frame_data[2];")
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
                        output.append(f"                        {value_name}_errors += 1;")
                        output.append(f"                        {value_name}_valid = 0;")
                    output.append("                    }")
                else:
                    output.append(f"                    // get single 16bit value")
                    output.append("                    data_len = frame_data[2];")
                    output.append(f"                    if (data_addr == {address} && data_len == {self.signal_values * 2}) {{")
                    output.append(f"                        value_{self.signal_name} = (frame_data[{3}]<<8) + (frame_data[{4}] & 0xFF);")
                    if vscale:
                        output.append(f"                        value_{self.signal_name} *= {vscale};")
                    output.append(f"                        value_{self.signal_name}_valid = 1;")
                    output.append("                    } else {")
                    output.append(f"                        value_{self.signal_name}_errors += 1;")
                    output.append(f"                        value_{self.signal_name}_valid = 0;")
                    output.append("                    }")
                output.append("                    break;")
                output.append("                }")
            sn += 1
        output.append("            }")

        output.append("        } else {")
        output.append('            printf("ERROR: CSUM: %d|%d != %d|%d\\n", crc & 0xFF, crc>>8 & 0xFF, frame_data[frame_len - 2], frame_data[frame_len - 1]);')
        output.append("        }")
        output.append('        // printf("rx frame %i %i: ", frame_id, frame_len);')
        output.append("        // for (n = 0; n < frame_len; n++) {")
        output.append('        //     printf("%i, ", frame_data[n]);')
        output.append("        // }")
        output.append('        // printf("\\n");')
        output.append("    }")
        return "\n".join(output)

    def frameio_tx_c(self):
        output = []

        output.append("    if (frame_timeout == 1) {")
        sn = 0
        for signal_name, signal_config in self.plugin_setup.get("config", {}).items():
            direction = signal_config["direction"]
            address = signal_config["address"]
            ctype = signal_config["type"]
            vscale = signal_config.get("scale", 1.0)
            self.signal_values = signal_config.get("values", 1)
            register = self.int2list(signal_config["register"])
            n_values = self.int2list(self.signal_values)
            self.signal_name = signal_name
            self.signal_address = address
            if direction == "input":
                if self.signal_values > 1:
                    output.append(f"            if ({self.instances_name}_signal_active == {sn}) {{")
                    for vn in range(0, self.signal_values):
                        value_name = f"value_{self.signal_name}_{vn}"
                        output.append(f"                {value_name}_valid = 0;")
                        output.append(f"                {value_name}_errors += 1;")
                    output.append("            }")
                else:
                    output.append(f"            // get single 16bit value")
                    output.append(f"            if ({self.instances_name}_signal_active == {sn}) {{")
                    output.append(f"                value_{signal_name}_valid = 0;")
                    output.append(f"                value_{signal_name}_errors += 1;")
                    output.append("            }")
            sn += 1

        output.append("        }")
        output.append("")

        output.append(f"        if ({self.instances_name}_signal_active < {len(self.plugin_setup.get('config', {})) - 1}) {{")
        output.append(f"            {self.instances_name}_signal_active++;")
        output.append("        } else {")
        output.append(f"            {self.instances_name}_signal_active = 0;")
        output.append("        }")
        output.append("")

        output.append(f"        switch ({self.instances_name}_signal_active) {{")
        sn = 0
        for signal_name, signal_config in self.plugin_setup.get("config", {}).items():
            direction = signal_config["direction"]
            timeout = signal_config.get("timeout", self.TIMEOUT)
            delay = signal_config.get("delay", 0)
            address = signal_config["address"]
            ctype = signal_config["type"]
            self.signal_values = signal_config.get("values", 1)
            register = self.int2list(signal_config["register"])
            n_values = self.int2list(self.signal_values)
            self.signal_name = signal_name
            self.signal_address = address

            output.append(f"            case {sn}: {{")
            output.append(f"                // {signal_name}")
            output.append(f"                delay = {delay};")
            output.append(f"                timeout = {timeout};")
            if direction == "output":
                if self.signal_values > 1:
                    if ctype == 15:
                        output.append(f"                // set 1bit values")
                    else:
                        output.append(f"                // set 16bit values")
                    output.append(f"                frame_data[0] = {address};")
                    output.append(f"                frame_data[1] = {ctype};")
                    output.append(f"                frame_data[2] = {register[0]};")
                    output.append(f"                frame_data[3] = {register[1]};")
                    output.append(f"                frame_data[4] = {n_values[0]};")
                    output.append(f"                frame_data[5] = {n_values[1]};")
                    output.append(f"                frame_data[6] = 1;")
                    if ctype == 15:
                        output.append(f"                uint8_t bitvalues = 0;")
                        for vn in range(0, self.signal_values):
                            value_name = f"{self.signal_name}_{vn}"
                            output.append(f"                if (value_{value_name} == 1) {{")
                            output.append(f"                    bitvalues |= (1<<{vn});")
                            output.append("                }")
                        output.append("                frame_data[7] = bitvalues;")
                        output.append("                frame_len = 8;")

                    else:
                        for vn in range(0, self.signal_values):
                            value_name = f"{self.signal_name}_{vn}"
                            output.append(f"                frame_data[{6 + vn * 2}] = (uint16_t)value_{value_name}>>8 & 0xFF;")
                            output.append(f"                frame_data[{7 + vn * 2}] = (uint16_t)value_{value_name} & 0xFF;")
                        output.append(f"                frame_len = {8 + vn * 2};")
                else:
                    if ctype == 5:
                        output.append(f"                // set coil value")
                    else:
                        output.append(f"                // set 16bit value")
                    output.append(f"                frame_data[0] = {address};")
                    output.append(f"                frame_data[1] = {ctype};")
                    output.append(f"                frame_data[2] = {register[0]};")
                    output.append(f"                frame_data[3] = {register[1]};")
                    if ctype == 5:
                        output.append(f"                if (value_{signal_name} == 1) {{")
                        output.append(f"                    frame_data[4] = 255;")
                        output.append(f"                    frame_data[5] = 0;")
                        output.append("                } else {")
                        output.append(f"                    frame_data[4] = 0;")
                        output.append(f"                    frame_data[5] = 0;")
                        output.append("                }")
                    else:
                        output.append(f"                frame_data[4] = (uint16_t)value_{signal_name}>>8 & 0xFF;")
                        output.append(f"                frame_data[5] = (uint16_t)value_{signal_name} & 0xFF;")
                    output.append(f"                frame_len = 6;")
            else:
                output.append(f"                // request 16bit value")
                output.append(f"                frame_data[0] = {address};")
                output.append(f"                frame_data[1] = {ctype};")
                output.append(f"                frame_data[2] = {register[0]};")
                output.append(f"                frame_data[3] = {register[1]};")
                output.append(f"                frame_data[4] = {n_values[0]};")
                output.append(f"                frame_data[5] = {n_values[1]};")
                output.append(f"                frame_len = 6;")

            output.append("                break;")
            output.append("            }")

            sn += 1
        output.append("        }")
        output.append("")

        output.append("")
        output.append("        uint8_t i = 0;")
        output.append("        uint16_t crc = 0xFFFF;")
        output.append("        for (i = 0; i < frame_len; i++) {")
        output.append("            crc = crc16_update(crc, frame_data[i]);")
        output.append("        }")
        output.append("        frame_data[frame_len] = crc & 0xFF;")
        output.append("        frame_data[frame_len + 1] = crc>>8 & 0xFF;")
        output.append("        frame_len += 2;")

        return "\n".join(output)
