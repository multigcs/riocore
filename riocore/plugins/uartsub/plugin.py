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
        self.TYPE = "sub_interface"
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

        self.INTERFACE = {
            "timeout": {
                "size": 1,
                "direction": "input",
            },
        }
        self.SIGNALS = {
            "timeout": {
                "direction": "input",
                "bool": True,
            },
        }
        self.OPTIONS = {
            "timeout": {
                "default": 100,
                "type": int,
                "min": 1,
                "max": 10000,
                "unit": "ms",
                "description": "timeout in ms",
            },
        }
        self.SUB_OPTIONS = {"baud": 2500000}

    @classmethod
    def component_loader(cls, instances):
        for sub_num, instance in enumerate(instances):
            if instance.SUBBOARD is None:
                # do not build, if no sub connected
                instance.INTERFACE = {}
                instance.PINDEFAULTS = {}
            instance.SUBNUM = sub_num

    def gateware_instances(self):
        if self.SUBBOARD is None:
            return None
        instances = self.gateware_instances_base()
        instance = instances[self.instances_name]
        instance_parameter = instance["parameter"]
        baud = int(self.SUB_OPTIONS["baud"])
        timeout = int(self.plugin_setup.get("timeout", self.OPTIONS["timeout"]["default"]))
        instance_parameter["BUFFER_SIZE_RX"] = f"SUB{self.SUBNUM}_BUFFER_SIZE_RX"
        instance_parameter["BUFFER_SIZE_TX"] = f"SUB{self.SUBNUM}_BUFFER_SIZE_TX"
        instance_parameter["MSGID"] = "32'h61746164"
        instance_parameter["ClkFrequency"] = self.system_setup["speed"]
        instance_parameter["Baud"] = baud
        timeout_cnt = self.system_setup["speed"] * timeout // 1000
        instance_parameter["Timeout"] = timeout_cnt
        instance_parameter["CSUM"] = 1
        instance["arguments"]["rx_data"] = f"sub{self.SUBNUM}_rx_data"
        instance["arguments"]["tx_data"] = f"sub{self.SUBNUM}_tx_data"
        instance["arguments"]["sync_in"] = "INTERFACE_SYNC_RISINGEDGE"
        return instances
