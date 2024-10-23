from riocore.plugins import PluginBase


class Plugin(PluginBase):
    def setup(self):
        self.NAME = "uart"
        self.INFO = "uart interface for host cominucation"
        self.DESCRIPTION = "simple uart interface, not usable for realtime stuff in LinuxCNC / only for testing"
        self.KEYWORDS = "serial uart interface"
        self.ORIGIN = "https://github.com/ChandulaNethmal/Implemet-a-UART-link-on-FPGA-with-verilog/tree/master"
        self.VERILOGS = ["uart.v", "uart_baud.v", "uart_rx.v", "uart_tx.v"]
        self.PINDEFAULTS = {
            "rx": {
                "direction": "input",
            },
            "tx": {
                "direction": "output",
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
        }
        self.TYPE = "interface"

    def gateware_instances(self):
        instances = self.gateware_instances_base()
        instance = instances[self.instances_name]
        instance_parameter = instance["parameter"]
        baud = int(self.system_setup.get("baud", self.OPTIONS["baud"]["default"]))
        instance_parameter["BUFFER_SIZE"] = self.system_setup["buffer_size"]
        instance_parameter["MSGID"] = "32'h74697277"
        instance_parameter["ClkFrequency"] = self.system_setup["speed"]
        instance_parameter["Baud"] = baud
        return instances
