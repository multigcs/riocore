import time

from riocore.plugins import PluginBase


class Plugin(PluginBase):
    def setup(self):
        self.NAME = "abs_encoder"
        self.INFO = "serial abs-encoder"
        self.KEYWORDS = "absolute angle encoder"
        self.ORIGIN = ""
        self.EXPERIMENTAL = True
        self.OPTIONS = {
            "node_type": {
                "default": "yaskawa",
                "type": "select",
                "options": [
                    "panasonic",
                    "stepperonline",
                    "t3d",
                    "yaskawa",
                    "rioencoder",
                ],
                "description": "encoder type",
            },
        }
        node_type = self.plugin_setup.get("node_type", self.option_default("node_type"))
        if node_type == "rioencoder":
            self.VERILOGS = ["rioencoder.v", "uart_baud.v", "uart_rx.v"]
            self.INFO = "serial abs-encoder"
            self.DESCRIPTION = "abs-encoder over rs485 (rx-only)"
            self.PINDEFAULTS = {
                "rx": {
                    "direction": "input",
                },
                "rw": {
                    "direction": "output",
                    "optional": True,
                },
            }
            self.INTERFACE = {
                "revs": {
                    "size": 32,
                    "direction": "input",
                },
                "angle": {
                    "size": 16,
                    "direction": "input",
                },
                "temperature": {
                    "size": 16,
                    "direction": "input",
                },
            }
            self.SIGNALS = {
                "revs": {
                    "direction": "input",
                    "format": "d",
                },
                "angle": {
                    "direction": "input",
                    "format": "0.1f",
                },
                "temperature": {
                    "direction": "input",
                    "unit": "°C",
                    "format": "0.1f",
                },
                "position": {
                    "direction": "input",
                    "format": "0.3f",
                },
                "rps": {
                    "direction": "input",
                    "format": "0.3f",
                },
                "rpm": {
                    "direction": "input",
                    "format": "0.3f",
                },
            }
            self._scale = 4096
            self.position_last = 0
            self.timer_last = time.time()
        elif node_type == "panasonic":
            self.VERILOGS = ["panasonic_abs.v", "uart_baud.v", "uart_rx.v", "uart_tx.v"]
            self.INFO = "serial abs-encoder"
            self.DESCRIPTION = """
abs-encoder over rs485

TODO: csum, pos/revs, cleanup

for Panasonic and some Bosch/Rexroth Servos with
mfe0017 encoder

FG      Shield      
VCC-    GND     Black
VCC+    5V      White
VB-     GND     Orange
VB+     3.3V    RED
SD+     RS485-A Blue
SD-     RS485-B Brown

Connector:
V+  V-
B-  SD+
B+  SD-  FG

"""
            self.OPTIONS.update(
                {
                    "delay": {
                        "default": 3,
                        "type": int,
                        "min": 1,
                        "max": 100,
                        "unit": "clocks",
                        "description": "clock delay for next manchester bit",
                    },
                    "delay_next": {
                        "default": 4,
                        "type": int,
                        "min": 1,
                        "max": 100,
                        "unit": "clocks",
                        "description": "clock delay for center of the next manchester bit",
                    },
                }
            )
            self.PINDEFAULTS = {
                "rx": {
                    "direction": "input",
                },
                "tx": {
                    "direction": "output",
                },
                "tx_enable": {
                    "direction": "output",
                },
                "debug_bit": {
                    "direction": "output",
                    "optional": True,
                },
            }
            self.INTERFACE = {
                "tmp1": {
                    "size": 8,
                    "direction": "input",
                },
                "tmp2": {
                    "size": 8,
                    "direction": "input",
                },
                "angle": {
                    "size": 16,
                    "direction": "input",
                },
                "position": {
                    "size": 32,
                    "direction": "input",
                },
                "csum": {
                    "size": 8,
                    "direction": "input",
                },
                "debug_data": {
                    "size": 32,
                    "direction": "input",
                },
                "cmd": {
                    "size": 8,
                    "direction": "output",
                },
            }
            self.SIGNALS = {
                "tmp1": {
                    "direction": "input",
                    "format": "d",
                },
                "tmp2": {
                    "direction": "input",
                    "format": "d",
                },
                "angle": {
                    "direction": "input",
                    "format": "d",
                },
                "position": {
                    "direction": "input",
                    "format": "d",
                },
                "revs": {
                    "direction": "input",
                    "format": "d",
                },
                "csum": {
                    "direction": "input",
                    "format": "0.3f",
                },
                "debug_data": {
                    "direction": "input",
                    "format": "d",
                },
                "cmd": {
                    "direction": "output",
                    "format": "d",
                },
            }
        elif node_type == "stepperonline":
            self.VERILOGS = ["stepperonline_abs.v", "uart_baud.v", "uart_rx.v", "uart_tx.v"]
            self.INFO = "serial abs-encoder stepperonline A6"
            self.DESCRIPTION = """
abs-encoder over rs485

17bit Absolute

Firewire-Connector:
* 1 5V
* 2 GND
* 3 NC
* 4 NC
* 5 PS+
* 6 PS-

"""
            self.PINDEFAULTS = {
                "rx": {
                    "direction": "input",
                },
                "tx": {
                    "direction": "output",
                },
                "tx_enable": {
                    "direction": "output",
                },
            }
            self.INTERFACE = {
                "tmp1": {
                    "size": 8,
                    "direction": "input",
                },
                "tmp2": {
                    "size": 8,
                    "direction": "input",
                },
                "revs": {
                    "size": 32,
                    "direction": "input",
                },
                "angle16": {
                    "size": 16,
                    "direction": "input",
                },
                "angle": {
                    "size": 32,
                    "direction": "input",
                },
            }
            self.SIGNALS = {
                "tmp1": {
                    "direction": "input",
                    "format": "d",
                },
                "tmp2": {
                    "direction": "input",
                    "format": "d",
                },
                "revs": {
                    "direction": "input",
                    "format": "d",
                },
                "angle16": {
                    "direction": "input",
                    "format": "d",
                },
                "angle": {
                    "direction": "input",
                    "format": "d",
                },
                "position": {
                    "direction": "input",
                    "format": "d",
                },
            }
        elif node_type == "t3d":
            self.VERILOGS = ["t3d_abs.v", "uart_baud.v", "uart_rx.v", "uart_tx.v"]
            self.INFO = "serial abs-encoder hltnc t3d"
            self.DESCRIPTION = """
abs-encoder over rs485

17bit Absolute

Firewire-Connector:
* 1 PS+
* 2 PS-
* 3 NC
* 4 NC
* 5 5V
* 6 GND
"""
            self.PINDEFAULTS = {
                "rx": {
                    "direction": "input",
                },
                "tx": {
                    "direction": "output",
                },
                "tx_enable": {
                    "direction": "output",
                },
            }
            self.INTERFACE = {
                "revs": {
                    "size": 32,
                    "direction": "input",
                },
                "angle16": {
                    "size": 16,
                    "direction": "input",
                },
                "angle": {
                    "size": 32,
                    "direction": "input",
                },
            }
            self.SIGNALS = {
                "revs": {
                    "direction": "input",
                    "format": "d",
                },
                "angle16": {
                    "direction": "input",
                    "format": "d",
                },
                "angle": {
                    "direction": "input",
                    "format": "d",
                },
                "position": {
                    "direction": "input",
                    "format": "d",
                },
            }
        elif node_type == "yaskawa":
            self.VERILOGS = ["yaskawa_abs.v"]
            self.INFO = "serial abs-encoder"
            self.DESCRIPTION = """
abs-encoder over rs485

angle scale: 16bit (65536)
position scale: 17bit (131072)

protocol in short:
    * RS485
    * manchester code
    * stuffing bit (after 5x1)
    * 16bit checksum

very time critical
on TangNano9k:
 "speed": "32400000",
 parameter DELAY=3, parameter DELAY_NEXT=4

"""
            self.OPTIONS.update(
                {
                    "delay": {
                        "default": 3,
                        "type": int,
                        "min": 1,
                        "max": 100,
                        "unit": "clocks",
                        "description": "clock delay for next manchester bit",
                    },
                    "delay_next": {
                        "default": 4,
                        "type": int,
                        "min": 1,
                        "max": 100,
                        "unit": "clocks",
                        "description": "clock delay for center of the next manchester bit",
                    },
                }
            )
            self.PINDEFAULTS = {
                "rx": {
                    "direction": "input",
                },
                "tx": {
                    "direction": "output",
                },
                "tx_enable": {
                    "direction": "output",
                },
                "debug_bit": {
                    "direction": "output",
                    "optional": True,
                },
                "rx_synced": {
                    "direction": "output",
                    "optional": True,
                },
            }
            self.INTERFACE = {
                "batt_error": {
                    "size": 1,
                    "direction": "input",
                },
                "temp": {
                    "size": 8,
                    "direction": "input",
                },
                # "scounter": {
                #     "size": 8,
                #     "direction": "input",
                # },
                # "fcounter": {
                #     "size": 16,
                #     "direction": "input",
                # },
                # "speed": {
                #     "size": 16,
                #     "direction": "input",
                # },
                # "fine_pos": {
                #     "size": 8,
                #     "direction": "input",
                # },
                "angle": {
                    "size": 16,
                    "direction": "input",
                },
                "position": {
                    "size": 32,
                    "direction": "input",
                },
                "csum": {
                    "size": 16,
                    "direction": "input",
                },
                "debug_data": {
                    "size": 32,
                    "direction": "input",
                },
            }
            self.SIGNALS = {
                "batt_error": {
                    "direction": "input",
                    "bool": True,
                },
                "temp": {
                    "direction": "input",
                    "format": "d",
                },
                # "scounter": {
                #     "direction": "input",
                #     "format": "d",
                # },
                # "fcounter": {
                #     "direction": "input",
                #     "format": "d",
                # },
                # "speed": {
                #     "direction": "input",
                #     "format": "d",
                # },
                # "fine_pos": {
                #     "direction": "input",
                #     "format": "d",
                # },
                "angle": {
                    "direction": "input",
                    "format": "0.2f",
                },
                "position": {
                    "direction": "input",
                    "format": "0.3f",
                },
                "csum": {
                    "direction": "input",
                    "format": "d",
                },
                "debug_data": {
                    "direction": "input",
                    "format": "d",
                },
            }
        self.angle_last = None

    def gateware_instances(self):
        instances = self.gateware_instances_base()
        instance = instances[self.instances_name]
        instance_parameter = instance["parameter"]
        node_type = self.plugin_setup.get("node_type", self.option_default("node_type"))
        if node_type == "rioencoder" or node_type == "panasonic" or node_type == "stepperonline" or node_type == "t3d":
            instance_parameter["ClkFrequency"] = self.system_setup["speed"]
        elif node_type == "yaskawa":
            instance_parameter["DELAY"] = int(self.plugin_setup.get("delay", self.OPTIONS["delay"]["default"]))
            instance_parameter["DELAY_NEXT"] = int(self.plugin_setup.get("delay_next", self.OPTIONS["delay_next"]["default"]))
        return instances

    def convert(self, signal_name, signal_setup, value):
        node_type = self.plugin_setup.get("node_type", self.option_default("node_type"))
        if node_type == "rioencoder":
            if signal_name == "temperature":
                value = value / 10.0
            elif signal_name == "angle":
                position = self.SIGNALS["revs"]["value"] * self._scale + value
                self.SIGNALS["position"]["value"] = position

                # calc rps/rpm
                diff = position - self.position_last
                self.position_last = position
                timer_new = time.time()
                timer_diff = timer_new - self.timer_last
                rps = diff / timer_diff / 4096
                self.timer_last = timer_new
                self.SIGNALS["rps"]["value"] = rps
                self.SIGNALS["rpm"]["value"] = rps * 60
                value = value * 360.0 / self._scale
        elif node_type == "panasonic":
            if signal_name == "angle":
                if self.angle_last is not None:
                    if value - self.angle_last > 30000:
                        self.SIGNALS["revs"]["value"] -= 1
                    elif value - self.angle_last < -30000:
                        self.SIGNALS["revs"]["value"] += 1
                self.angle_last = value
                value = value * 360.0 / 65536
        elif node_type == "stepperonline":
            if signal_name == "angle16":
                value = value * 360.0 / 65536
            elif signal_name == "angle":
                self.SIGNALS["position"]["value"] = self.SIGNALS["revs"]["value"] * 131072 + value
        elif node_type == "t3d":
            if signal_name == "angle16":
                value = value * 360.0 / 65536
            elif signal_name == "angle":
                self.SIGNALS["position"]["value"] = self.SIGNALS["revs"]["value"] * 131072 + value
            return value
        elif node_type == "yaskawa":
            if signal_name == "angle":
                value = value * 360.0 / 65536
        return value

    def convert_c(self, signal_name, signal_setup):
        node_type = self.plugin_setup.get("node_type", self.option_default("node_type"))
        if node_type == "rioencoder":
            if signal_name == "temperature":
                return "value = value / 10;"
            if signal_name == "angle":
                varname_revs = self.SIGNALS["revs"]["varname"]
                varname_pos = self.SIGNALS["position"]["varname"]
                varname_rps = self.SIGNALS["rps"]["varname"]
                varname_rpm = self.SIGNALS["rpm"]["varname"]
                return f"""

        // calc position
        float position_value = *data->{varname_revs} * {self._scale} + raw_value;

        // calc rps/rpm
        static uint8_t pcnt = 0;
        static float last_rpssum = 0;
        static float last_pos = 0;
        static float diff_sum = 0;
        static float duration_sum = 0.0;
        float diff = position_value - last_pos;
        last_pos = position_value;
        diff_sum += diff;
        duration_sum += *data->duration;
        pcnt++;
        if (pcnt == 100) {{
            last_rpssum = diff_sum / duration_sum / 4096;
            pcnt = 0;
            duration_sum = 0;
            diff_sum = 0;
        }}
        *data->{varname_rps} = last_rpssum;
        *data->{varname_rpm} = last_rpssum * 60;

        // pos scale/offset
        position_value = position_value + *data->{varname_pos}_OFFSET;
        position_value = position_value / *data->{varname_pos}_SCALE;
        *data->{varname_pos} = position_value;

        // calc angle (0-360°)
        value = value * 360 / {self._scale};
                """
            return ""
