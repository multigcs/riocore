import os

from riocore.checksums import crc8, crc16
from riocore.plugins import PluginBase


class Plugin(PluginBase):
    def setup(self):
        self.NAME = "uartbridge"
        self.INFO = "uart bridge - experimental - python only"
        self.KEYWORDS = "serial uart"
        self.DESCRIPTION = "uart bridge to send and receive custom frames via uart port"
        self.ORIGIN = "https://github.com/ChandulaNethmal/Implemet-a-UART-link-on-FPGA-with-verilog/tree/master"
        self.VERILOGS = ["uartbridge.v", "uart_baud.v", "uart_rx.v", "uart_tx.v"]
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
            "tx_frame": {
                "default": "tx1:u8|tx2:u8",
                "type": str,
                "description": "tx frame format",
            },
            "rx_frame": {
                "default": "rx1:u8|rx2:u8",
                "type": str,
                "description": "rx frame format",
            },
        }
        self.SIGNALS = {}
        self.TYPE = "frameio"
        self.DYNAMIC_SIGNALS = True
        self.TIMEOUT = 1000.0
        self.DELAY = 0.0

        self.rx_buffersize = 3 * 8
        self.tx_buffersize = 2 * 8

        self.tx_frame = self.plugin_setup.get("tx_frame", self.OPTIONS["tx_frame"]["default"])
        self.rx_frame = self.plugin_setup.get("rx_frame", self.OPTIONS["rx_frame"]["default"])

        for part in self.tx_frame.split("|"):
            if part.startswith(":crc"):
                self.SIGNALS["tx_csum"] = {
                    "direction": "input",
                    "csum": part[1:],
                }
                if part[1:] == "crc8":
                    self.tx_buffersize += 8
                elif part[1:] == "crc16":
                    self.tx_buffersize += 16
                continue

            if ":" not in part:
                continue

            signal_name, signal_type = part.split(":")
            signal_size = 8
            signal_bfmt = "lsb"
            signal_signed = True
            if signal_type[0] == "u":
                signal_type = signal_type[1:]
                signal_signed = False
            elif signal_type[0] == "s":
                signal_type = signal_type[1:]
                signal_signed = True
            if signal_type[-1] == "l":
                signal_type = signal_type[:-1]
                signal_bfmt = "lsb"
            elif signal_type[-1] == "m":
                signal_type = signal_type[:-1]
                signal_bfmt = "msb"
            signal_size = int(signal_type)

            self.tx_buffersize += signal_size

            vmin = 0
            vmax = 2**signal_size - 1
            if signal_signed:
                vmin = -(vmax // 2)
                vmax = vmax // 2

            self.SIGNALS[signal_name] = {
                "direction": "output",
                "signal_signed": signal_signed,
                "signal_size": signal_size,
                "signal_bfmt": signal_bfmt,
                "min": vmin,
                "max": vmax,
            }

        for part in self.rx_frame.split("|"):
            if part.startswith(":crc"):
                self.SIGNALS["rx_csum"] = {
                    "direction": "input",
                    "csum": part[1:],
                }
                if part[1:] == "crc8":
                    self.rx_buffersize += 8
                elif part[1:] == "crc16":
                    self.rx_buffersize += 16
                continue

            if ":" not in part:
                continue

            signal_name, signal_type = part.split(":")
            signal_size = 8
            signal_bfmt = "lsb"
            signal_signed = True
            if signal_type[0] == "u":
                signal_type = signal_type[1:]
                signal_signed = False
            elif signal_type[0] == "s":
                signal_type = signal_type[1:]
                signal_signed = True
            if signal_type[-1] == "l":
                signal_type = signal_type[:-1]
                signal_bfmt = "lsb"
            elif signal_type[-1] == "m":
                signal_type = signal_type[:-1]
                signal_bfmt = "msb"
            signal_size = int(signal_type)

            self.rx_buffersize += signal_size

            self.SIGNALS[signal_name] = {
                "direction": "input",
                "signal_size": signal_size,
                "signal_bfmt": signal_bfmt,
                "signal_signed": signal_signed,
            }

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

    def gateware_instances(self):
        instances = self.gateware_instances_base()
        instance = instances[self.instances_name]
        instance_parameter = instance["parameter"]
        baud = int(self.plugin_setup.get("baud", self.OPTIONS["baud"]["default"]))
        instance_parameter["RX_BUFFERSIZE"] = self.plugin_setup.get("rx_buffersize", self.OPTIONS["rx_buffersize"]["default"])
        instance_parameter["TX_BUFFERSIZE"] = self.plugin_setup.get("tx_buffersize", self.OPTIONS["tx_buffersize"]["default"])
        instance_parameter["ClkFrequency"] = self.system_setup["speed"]
        instance_parameter["Baud"] = baud
        self.arduino_example()
        return instances

    def frameio_rx(self, frame_new, frame_id, frame_len, frame_data):
        if frame_new:
            # print(f"rx frame {frame_id} {frame_len}: {frame_data}")
            frame_check = True

            if frame_len != self.rx_buffersize // 8 - 3:
                print(f"ERROR: {self.NAME}: wrong frame size: {frame_len} != {self.rx_buffersize // 8 - 3}")
                return
            if len(frame_data) != self.rx_buffersize // 8 - 3:
                print(f"ERROR: {self.NAME}: wrong frame size: {frame_len} != {self.rx_buffersize // 8 - 3}")
                return

            if "rx_csum" in self.signals():
                csum_type = self.signals()["rx_csum"]["csum"]
                if csum_type == "crc8":
                    csum = crc8()
                elif csum_type == "crc16":
                    csum = crc16()

                frame_check = False
                frame_data_csum = frame_data.copy()
                for signal_name, signal_setup in self.signals().items():
                    if signal_setup["direction"] == "input" and signal_name != "tx_csum":
                        if signal_name == "rx_csum":
                            csum_calc = csum.intdigest()
                            csum_org = frame_data_csum
                            if csum_calc == csum_org:
                                frame_check = True
                            else:
                                print(f"ERROR: {self.NAME}: CSUM: {csum_calc} != {csum_org}")
                            csum_val = 0
                            for part in csum_calc:
                                csum_val = csum_val << 8
                                csum_val += part
                            signal_setup["value"] = csum_val

                        else:
                            value = 0
                            signal_size = signal_setup["signal_size"]
                            signal_bfmt = signal_setup["signal_bfmt"]
                            bytesize = signal_size // 8
                            if signal_bfmt == "lsb":
                                for byte in range(0, bytesize):
                                    byte_value = frame_data_csum.pop(0)
                                    csum.update(byte_value)
                            else:
                                for byte in range(0, signal_size // 8):
                                    byte_value = frame_data_csum.pop(0)
                                    csum.update(byte_value)

            if frame_check:
                for signal_name, signal_setup in self.signals().items():
                    if signal_setup["direction"] == "input":
                        if signal_name != "rx_csum" and signal_name != "tx_csum":
                            value = 0
                            signal_size = signal_setup["signal_size"]
                            signal_bfmt = signal_setup["signal_bfmt"]
                            bytesize = signal_size // 8
                            if signal_bfmt == "lsb":
                                for byte in range(0, bytesize):
                                    byte_value = frame_data.pop(0)
                                    value += byte_value << (8 * byte)
                            else:
                                for byte in range(0, signal_size // 8):
                                    byte_value = frame_data.pop(0)
                                    value += byte_value << (8 * (bytesize - byte - 1))
                            signal_setup["value"] = value

    def frameio_tx(self, frame_ack, frame_timeout):
        # if frame_ack:
        #    print("ACK")
        # if frame_timeout:
        #   print("TIMEOUT")
        frame_data = []
        for signal_name, signal_setup in self.signals().items():
            if signal_name == "tx_csum":
                csum_type = signal_setup["csum"]
                if csum_type == "crc8":
                    csum = crc8()
                elif csum_type == "crc16":
                    csum = crc16()
                csum.update(frame_data)
                frame_data += csum.intdigest()

                csum_val = 0
                for part in csum.intdigest():
                    csum_val = csum_val << 8
                    csum_val += part
                signal_setup["value"] = csum_val

            elif signal_setup["direction"] == "output":
                value = signal_setup["value"]
                signal_size = signal_setup["signal_size"]
                signal_bfmt = signal_setup["signal_bfmt"]
                bytesize = signal_size // 8
                if signal_bfmt == "lsb":
                    for byte in range(0, bytesize):
                        byte_value = (value >> (8 * byte)) & 0xFF
                        frame_data.append(byte_value)
                else:
                    for byte in range(0, signal_size // 8):
                        byte_value = (value >> (8 * (bytesize - byte - 1))) & 0xFF
                        frame_data.append(byte_value)

        # print(f"tx frame 00 {len(frame_data)}: {frame_data}")
        return frame_data

    def frameio_rx_c(self):
        return """
        if (frame_new == 1) {
            uint8_t n = 0;
            printf("rx frame %i %i: ", frame_id, frame_len);
            for (n = 0; n < frame_len; n++) {
                printf("%i, ", frame_data[n]);
            }
            printf("\\n");
        }
        """

    def frameio_tx_c(self):
        return """
        frame_len = 5;
        frame_data[2] = 'A';
        frame_data[3] = 'B';
        frame_data[4] = 'C';
        frame_data[5] = 'D';
        frame_data[6] = 10;
        """

    def arduino_example(self):
        output = []
        baud = int(self.plugin_setup.get("baud", self.OPTIONS["baud"]["default"]))

        output.append("")
        output.append("#include <LiquidCrystal_I2C.h>")
        output.append("#include <CRC8.h>")
        output.append("#include <CRC.h>")
        output.append("")
        output.append("LiquidCrystal_I2C lcd(0x27, 20, 4);")
        output.append("CRC8 crc;")
        output.append("")
        output.append(f"#define RX_LEN {self.rx_buffersize // 8 - 3}")
        output.append(f"#define TX_LEN {self.tx_buffersize // 8 - 2}")
        output.append("")
        output.append("typedef struct rx_data_t {")
        for signal_name, signal_setup in self.signals().items():
            if signal_setup["direction"] == "output":
                if signal_name != "rx_csum" and signal_name != "tx_csum":
                    signal_size = signal_setup["signal_size"]
                    output.append(f"    uint{signal_size}_t {signal_name};")
        output.append("    uint8_t csum;")
        output.append("};")
        output.append("")
        output.append("typedef struct tx_data_t {")
        for signal_name, signal_setup in self.signals().items():
            if signal_setup["direction"] == "input":
                if signal_name != "rx_csum" and signal_name != "tx_csum":
                    signal_size = signal_setup["signal_size"]
                    output.append(f"    uint{signal_size}_t {signal_name};")
        output.append("    uint8_t csum;")
        output.append("};")
        output.append("")
        output.append("typedef union rx_frame_t {")
        output.append("    rx_data_t data;")
        output.append("    uint8_t buffer[RX_LEN];")
        output.append("};")
        output.append("")
        output.append("typedef union tx_frame_t {")
        output.append("    tx_data_t data;")
        output.append("    uint8_t buffer[TX_LEN];")
        output.append("};")
        output.append("")
        output.append("rx_frame_t rx_frame;")
        output.append("tx_frame_t tx_frame;")
        output.append("")
        output.append("char tmp_str[24];")
        output.append("int32_t value = 0;")
        output.append("")
        output.append("void setup() {")
        output.append(f"    Serial.begin({baud});")
        output.append("    lcd.init();")
        output.append("    lcd.backlight();")
        output.append("    lcd.setCursor(0, 0);")
        output.append('    lcd.print("LinuxCNC - RIO");')
        output.append("}")
        output.append("")
        output.append("void loop() {")
        output.append("    // rx")
        output.append("    Serial.readBytes(rx_frame.buffer, RX_LEN);")
        output.append("    crc.restart();")
        output.append("    uint8_t csum = calcCRC8(rx_frame.buffer, RX_LEN-1);")
        output.append("")
        output.append("    if (csum == rx_frame.data.csum) {")
        line_n = 0
        for signal_name, signal_setup in self.signals().items():
            if signal_setup["direction"] == "output":
                if signal_name != "rx_csum" and signal_name != "tx_csum":
                    signal_size = signal_setup["signal_size"]
                    output.append(f'        sprintf(tmp_str, "{signal_name:10} %9d", rx_frame.data.{signal_name});')
                    output.append(f"        lcd.setCursor(0, {line_n});")
                    output.append("        lcd.print(tmp_str);")
                    output.append("")
                    line_n += 1
        output.append("    } else {")
        output.append('        sprintf(tmp_str, "CSUMERROR %03d != %03d   ", csum, rx_frame.data.csum);')
        output.append("        lcd.setCursor(0, 3);")
        output.append("        lcd.print(tmp_str);")
        output.append("    }")
        output.append("")
        output.append("    // tx")
        value_n = 0
        for signal_name, signal_setup in self.signals().items():
            if signal_setup["direction"] == "input":
                if signal_name != "rx_csum" and signal_name != "tx_csum":
                    signal_size = signal_setup["signal_size"]
                    output.append(f"    tx_frame.data.{signal_name} = {value_n + 1};")
                    value_n += 1
        output.append("    crc.restart();")
        output.append("    uint8_t tx_csum = calcCRC8(tx_frame.buffer, TX_LEN-1);")
        output.append("    tx_frame.data.csum = tx_csum;")
        output.append("    Serial.write(tx_frame.buffer, TX_LEN);")
        output.append("")
        output.append("}")
        output.append("")

        folder = f"{self.system_setup['output_path']}/arduino_example_{self.instances_name}"
        os.makedirs(f"{folder}/src/", exist_ok=True)
        open(f"{folder}/src/main.ino", "w").write("\n".join(output))
