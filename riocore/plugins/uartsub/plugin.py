from riocore.plugins import PluginBase


class Plugin(PluginBase):
    def setup(self):
        self.NAME = "uartsub"
        self.INFO = "uartsub interface for host cominucation"
        self.DESCRIPTION = "simple uartsub interface, not usable for realtime stuff in LinuxCNC / only for testing"
        self.KEYWORDS = "serial uartsub interface"
        self.ORIGIN = "https://github.com/ChandulaNethmal/Implemet-a-UART-link-on-FPGA-with-verilog/tree/master"
        self.VERILOGS = ["uartsub.v", "uart_baud.v", "uart_rx.v", "uart_tx.v"]
        self.NEEDS = ["fpga"]
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
            "SAT:OUT": {
                "direction": "output",
                "edge": "source",
                "bus": True,
                "type": ["SATCON"],
            },
        }
        self.OPTIONS = {
            "baud": {
                "default": 2500000,
                "type": int,
                "min": 9600,
                "max": 10000000,
                "unit": "bit/s",
                "description": "serial baud rate",
            },
        }
        self.COMPONENT = "sub_interface"

    def update_pins(self, parent):
        for connected_pin in parent.get_all_plugin_pins(configured=True, prefix=self.instances_name):
            plugin_instance = connected_pin["instance"]
            self.SUBBOARD = plugin_instance.master

    @classmethod
    def component_loader(cls, instances):
        for sub_num, instance in enumerate(instances):
            instance.SUBNUM = sub_num

    def gateware_instances(self):
        instances = self.gateware_instances_base()
        instance = instances[self.instances_name]
        instance_parameter = instance["parameter"]
        baud = int(self.plugin_setup.get("baud", self.OPTIONS["baud"]["default"]))
        instance_parameter["BUFFER_SIZE_RX"] = f"SUB{self.SUBNUM}_BUFFER_SIZE_RX"
        instance_parameter["BUFFER_SIZE_TX"] = f"SUB{self.SUBNUM}_BUFFER_SIZE_TX"
        instance_parameter["MSGID"] = "32'h64617461"
        instance_parameter["ClkFrequency"] = self.system_setup["speed"]
        instance_parameter["Baud"] = baud
        instance_parameter["CSUM"] = 1
        instance["arguments"]["rx_data"] = f"sub{self.SUBNUM}_rx_data"
        instance["arguments"]["tx_data"] = f"sub{self.SUBNUM}_tx_data"
        instance["arguments"]["sync"] = "INTERFACE_SYNC_RISINGEDGE"
        return instances
