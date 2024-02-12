from struct import *

from riocore.plugins import PluginBase


class crc8(object):

    digest_size = 1
    block_size = 1

    _table = [
        0x00,
        0x07,
        0x0E,
        0x09,
        0x1C,
        0x1B,
        0x12,
        0x15,
        0x38,
        0x3F,
        0x36,
        0x31,
        0x24,
        0x23,
        0x2A,
        0x2D,
        0x70,
        0x77,
        0x7E,
        0x79,
        0x6C,
        0x6B,
        0x62,
        0x65,
        0x48,
        0x4F,
        0x46,
        0x41,
        0x54,
        0x53,
        0x5A,
        0x5D,
        0xE0,
        0xE7,
        0xEE,
        0xE9,
        0xFC,
        0xFB,
        0xF2,
        0xF5,
        0xD8,
        0xDF,
        0xD6,
        0xD1,
        0xC4,
        0xC3,
        0xCA,
        0xCD,
        0x90,
        0x97,
        0x9E,
        0x99,
        0x8C,
        0x8B,
        0x82,
        0x85,
        0xA8,
        0xAF,
        0xA6,
        0xA1,
        0xB4,
        0xB3,
        0xBA,
        0xBD,
        0xC7,
        0xC0,
        0xC9,
        0xCE,
        0xDB,
        0xDC,
        0xD5,
        0xD2,
        0xFF,
        0xF8,
        0xF1,
        0xF6,
        0xE3,
        0xE4,
        0xED,
        0xEA,
        0xB7,
        0xB0,
        0xB9,
        0xBE,
        0xAB,
        0xAC,
        0xA5,
        0xA2,
        0x8F,
        0x88,
        0x81,
        0x86,
        0x93,
        0x94,
        0x9D,
        0x9A,
        0x27,
        0x20,
        0x29,
        0x2E,
        0x3B,
        0x3C,
        0x35,
        0x32,
        0x1F,
        0x18,
        0x11,
        0x16,
        0x03,
        0x04,
        0x0D,
        0x0A,
        0x57,
        0x50,
        0x59,
        0x5E,
        0x4B,
        0x4C,
        0x45,
        0x42,
        0x6F,
        0x68,
        0x61,
        0x66,
        0x73,
        0x74,
        0x7D,
        0x7A,
        0x89,
        0x8E,
        0x87,
        0x80,
        0x95,
        0x92,
        0x9B,
        0x9C,
        0xB1,
        0xB6,
        0xBF,
        0xB8,
        0xAD,
        0xAA,
        0xA3,
        0xA4,
        0xF9,
        0xFE,
        0xF7,
        0xF0,
        0xE5,
        0xE2,
        0xEB,
        0xEC,
        0xC1,
        0xC6,
        0xCF,
        0xC8,
        0xDD,
        0xDA,
        0xD3,
        0xD4,
        0x69,
        0x6E,
        0x67,
        0x60,
        0x75,
        0x72,
        0x7B,
        0x7C,
        0x51,
        0x56,
        0x5F,
        0x58,
        0x4D,
        0x4A,
        0x43,
        0x44,
        0x19,
        0x1E,
        0x17,
        0x10,
        0x05,
        0x02,
        0x0B,
        0x0C,
        0x21,
        0x26,
        0x2F,
        0x28,
        0x3D,
        0x3A,
        0x33,
        0x34,
        0x4E,
        0x49,
        0x40,
        0x47,
        0x52,
        0x55,
        0x5C,
        0x5B,
        0x76,
        0x71,
        0x78,
        0x7F,
        0x6A,
        0x6D,
        0x64,
        0x63,
        0x3E,
        0x39,
        0x30,
        0x37,
        0x22,
        0x25,
        0x2C,
        0x2B,
        0x06,
        0x01,
        0x08,
        0x0F,
        0x1A,
        0x1D,
        0x14,
        0x13,
        0xAE,
        0xA9,
        0xA0,
        0xA7,
        0xB2,
        0xB5,
        0xBC,
        0xBB,
        0x96,
        0x91,
        0x98,
        0x9F,
        0x8A,
        0x8D,
        0x84,
        0x83,
        0xDE,
        0xD9,
        0xD0,
        0xD7,
        0xC2,
        0xC5,
        0xCC,
        0xCB,
        0xE6,
        0xE1,
        0xE8,
        0xEF,
        0xFA,
        0xFD,
        0xF4,
        0xF3,
    ]

    def __init__(self, initial_string=b"", initial_start=0x00):
        """Create a new crc8 hash instance."""
        self._sum = initial_start
        self._initial_start = initial_start
        self.update(initial_string)

    def hexdigest(self):
        """Return digest() as hexadecimal string.

        Like digest() except the digest is returned as a string of double
        length, containing only hexadecimal digits. This may be used to
        exchange the value safely in email or other non-binary environments.
        """
        return hex(self._sum)[2:].zfill(2)

    def intdigest(self):
        """Return digest() as hexadecimal string.

        Like digest() except the digest is returned as a string of double
        length, containing only hexadecimal digits. This may be used to
        exchange the value safely in email or other non-binary environments.
        """
        return int(self._sum)

    def update(self, bytes_):
        if isinstance(bytes_, str):
            raise TypeError("Unicode-objects must be encoded before" " hashing")
        elif not isinstance(bytes_, (bytes, bytearray)):

            if isinstance(bytes_, (list)):
                bytes_ = bytearray(bytes_)
            elif isinstance(bytes_, (int)):
                bytes_ = bytearray([bytes_])
            else:
                raise TypeError("object supporting the buffer API required")
        table = self._table
        _sum = self._sum
        for byte in bytes_:
            # print(int(byte))
            _sum = table[_sum ^ byte]
        self._sum = _sum

    def digest(self):
        return bytes([self._sum])

    def copy(self):
        """Return a copy ("clone") of the hash object.

        This can be used to efficiently compute the digests of strings that
        share a common initial substring.
        """
        crc = crc8()
        crc._sum = self._sum
        return crc

    def reset(self):
        """Resets the hash object to its initial state."""
        self._sum = self._initial_start


class Plugin(PluginBase):
    def setup(self):
        self.NAME = "uartbridge"
        self.VERILOGS = ["uartbridge.v", "uart_baud.v", "uart_rx.v", "uart_tx.v"]
        self.PINDEFAULTS = {
            "tx": {
                "direction": "output",
            },
            "rx": {
                "direction": "input",
            },
        }
        self.OPTIONS = {
            "baud": {
                "default": 300,
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
                "default": "",
                "type": str,
                "description": "tx frame format",
            },
            "rx_frame": {
                "default": "",
                "type": str,
                "description": "rx frame format",
            },
        }
        self.INTERFACE = {
            "rxdata": {
                "size": self.plugin_setup.get("rx_buffersize", self.OPTIONS["rx_buffersize"]["default"]),
                "direction": "input",
            },
            "txdata": {
                "size": self.plugin_setup.get("tx_buffersize", self.OPTIONS["tx_buffersize"]["default"]),
                "direction": "output",
            },
        }
        self.SIGNALS = {}
        self.TYPE = "frameio"
        self.TIMEOUT = 1000.0
        self.INFO = "uart bridge"
        self.DESCRIPTION = ""

        self.tx_frame = self.plugin_setup.get("tx_frame", self.OPTIONS["tx_frame"]["default"])
        self.rx_frame = self.plugin_setup.get("rx_frame", self.OPTIONS["rx_frame"]["default"])

        for part in self.tx_frame.split("|"):
            if part.startswith(":crc"):
                self.SIGNALS["tx_csum"] = {
                    "direction": "output",
                    "csum": part[1:],
                }
                continue

            signal_name, signal_type = part.split(":")
            signal_size = 8
            signal_bfmt = "msb"
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
            signal_size = int(signal_type)

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

            self.SIGNALS[signal_name] = {
                "direction": "input",
                "signal_size": signal_size,
                "signal_bfmt": signal_bfmt,
                "signal_signed": signal_signed,
            }

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

    def frameio_rx(self, frame_new, frame_id, frame_len, frame_data):
        if frame_new:
            # print(f"rx frame {frame_id} {frame_len}: {frame_data}")
            frame_check = True
            if "rx_csum" in self.signals():
                csum_type = self.signals()["rx_csum"]["csum"]
                if csum_type == "crc8":
                    csum = crc8()

                frame_check = False
                frame_data_csum = frame_data.copy()
                for signal_name, signal_setup in self.signals().items():
                    if signal_setup["direction"] == "input":
                        if signal_name == "rx_csum":
                            csum_calc = csum.intdigest()
                            csum_org = frame_data_csum.pop(0)
                            if csum_calc == csum_org:
                                frame_check = True
                            else:
                                print("ERROR: CSUM: ", csum_calc, csum_org)
                            signal_setup["value"] = csum_calc
                        else:
                            value = 0
                            signal_size = signal_setup["signal_size"]
                            signal_bfmt = signal_setup["signal_bfmt"]
                            signal_signed = signal_setup["signal_signed"]
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
                        if signal_name != "rx_csum":
                            value = 0
                            signal_size = signal_setup["signal_size"]
                            signal_bfmt = signal_setup["signal_bfmt"]
                            signal_signed = signal_setup["signal_signed"]
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
        #    print("TIMEOUT")
        frame_data = []
        for signal_name, signal_setup in self.signals().items():
            if signal_setup["direction"] == "output":
                if signal_name == "tx_csum":
                    if signal_setup["csum"] == "crc8":
                        csum = crc8()
                        csum.update(frame_data)
                        frame_data.append(csum.intdigest())
                else:
                    value = signal_setup["value"]
                    signal_size = signal_setup["signal_size"]
                    signal_bfmt = signal_setup["signal_bfmt"]
                    signal_signed = signal_setup["signal_signed"]
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
