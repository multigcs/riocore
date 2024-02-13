import os
from struct import *

from riocore.checksums import crc8, crc16
from riocore.plugins import PluginBase


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
        self.TIMEOUT = 10.0
        self.INFO = "uart bridge"
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

        for signal_name, signal_config in self.plugin_setup.get("signals", {}).items():
            self.SIGNALS[signal_name] = {
                "direction": signal_config["direction"],
                "unit": signal_config.get("unit", ""),
                "scale": signal_config.get("scale"),
                "format": signal_config.get("format"),
            }
            self.SIGNALS[f"{signal_name}_valid"] = {
                "direction": "input",
                "bool": True,
                "validation": True,
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
        self.signal_active = 0
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
        if frame_new:
            if frame_len > 4:
                address = frame_data[0]
                ctype = frame_data[1]
                data_len = frame_data[2]
                csum = crc16()
                cmd = []
                csum.update(frame_data[:-2])
                csum_calc = csum.intdigest()
                if csum_calc != frame_data[-2:]:
                    print("ERROR: modbus CSUM failed {csum_calc} != {frame_data[-2:]}")
                else:
                    if self.signal_name not in self.SIGNALS:
                        print("ERROR: no signal_config: {self.signal_name}")
                    else:
                        signal_config = self.SIGNALS[self.signal_name].get("userconfig", {})
                        signal_address = signal_config.get("address")
                        if address != signal_address:
                            print(f"ERROR: wrong address {address} != {signal_address}")
                        else:
                            self.SIGNALS[self.signal_name]["value"] = self.list2int(frame_data[3:-2])
                            self.SIGNALS[f"{self.signal_name}_valid"]["value"] = 1

            # print(f"rx frame {self.signal_active} {frame_id} {frame_len}: {frame_data}")

    def frameio_tx(self, frame_ack, frame_timeout):
        # if frame_ack:
        #    print("ACK")
        if frame_timeout:
            if f"{self.signal_name}_valid" in self.SIGNALS:
                self.SIGNALS[f"{self.signal_name}_valid"]["value"] = 0

        if self.signal_active < len(self.plugin_setup.get("signals", {})) - 1:
            self.signal_active += 1
        else:
            self.signal_active = 0

        csum = crc16()
        cmd = []

        sn = 0
        for signal_name, signal_config in self.plugin_setup.get("signals", {}).items():
            if sn == self.signal_active:
                address = signal_config["address"]
                ctype = signal_config["type"]
                register = self.int2list(signal_config["register"])
                n_values = self.int2list(1)
                self.signal_name = signal_name
                self.signal_address = address
                cmd = [address, ctype] + register + n_values
            sn += 1

        csum.update(cmd)
        csum_calc = csum.intdigest()
        frame_data = cmd + csum_calc

        # print(f"tx frame -- {len(frame_data)}: {frame_data}")
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
