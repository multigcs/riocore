from riocore.plugins import PluginBase


class Plugin(PluginBase):
    def setup(self):
        self.NAME = "uart"
        self.INFO = "uart interface for host cominucation"
        self.DESCRIPTION = "simple uart interface, not usable for realtime stuff in LinuxCNC / only for testing"
        self.KEYWORDS = "serial uart interface"
        self.ORIGIN = "https://github.com/ChandulaNethmal/Implemet-a-UART-link-on-FPGA-with-verilog/tree/master"
        self.NEEDS = ["fpga"]
        self.VERILOGS = ["uart.v", "uart_baud.v", "uart_rx.v", "uart_tx.v"]
        self.PINDEFAULTS = {
            "rx": {
                "direction": "input",
            },
            "tx": {
                "direction": "output",
            },
            "tx_enable": {
                "direction": "output",
                "optional": True,
                "descruption": "for RS485 mode",
            },
            "SAT": {
                "direction": "output",
                "edge": "target",
                "type": ["SATCON"],
                "optional": True,
                "bus": True,
            },
        }
        self.OPTIONS = {
            "baud": {
                "default": 1000000,
                "type": int,
                "min": 9600,
                "max": 10000000,
                "unit": "bit/s",
                "description": "serial baud rate",
            },
            "uart": {
                "default": "/dev/ttyUSB0",
                "type": str,
                "description": "serial device (if connected to host)",
            },
            "csum": {
                "default": True,
                "type": bool,
                "description": "activate checksums",
            },
            "async": {
                "default": False,
                "type": bool,
                "description": "async",
            },
            "frame": {
                "default": "full",
                "type": "select",
                "options": ["full", "no_timestamp", "no_header", "minimum"],
                "description": "frame size",
            },
            "debug": {
                "default": False,
                "type": bool,
                "description": "always response",
            },
        }
        self.TYPE = "interface"
        self.HOST_INTERFACE = "UART"

    def gateware_instances(self):
        instances = self.gateware_instances_base()
        instance = instances[self.instances_name]
        instance_parameter = instance["parameter"]
        frame = self.plugin_setup.get("frame", self.OPTIONS["frame"]["default"])
        csum = self.plugin_setup.get("csum", self.OPTIONS["csum"]["default"])
        baud = int(self.plugin_setup.get("baud", self.OPTIONS["baud"]["default"]))
        debug = self.plugin_setup.get("debug", self.OPTIONS["debug"]["default"])
        instance_parameter["BUFFER_SIZE_RX"] = "BUFFER_SIZE_RX"
        instance_parameter["BUFFER_SIZE_TX"] = "BUFFER_SIZE_TX"
        if frame in {"no_header", "minimum"}:
            instance_parameter["MSGID"] = "0"
        else:
            instance_parameter["MSGID"] = "32'h74697277"
        instance_parameter["ClkFrequency"] = self.system_setup["speed"]
        instance_parameter["Baud"] = baud
        instance_parameter["CSUM"] = int(csum)
        instance_parameter["DEBUG"] = int(debug)
        return instances
