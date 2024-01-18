from riocore.plugins import PluginBase


class Plugin(PluginBase):
    def setup(self):
        self.NAME = "uart"
        self.VERILOGS = ["uart.v", "uart_baud.v", "uart_rx.v", "uart_tx.v"]
        self.PINDEFAULTS = {
            "rx": {
                "direction": "input",
                "invert": False,
                "pullup": False,
            },
            "tx": {
                "direction": "output",
                "invert": False,
                "pullup": False,
                "optional": True,
            },
        }
        self.TYPE = "interface"

    def gateware_instances(self):
        instances = self.gateware_instances_base()

        instance = instances[self.instances_name]
        instance_predefines = instance["predefines"]
        instance_parameter = instance["parameter"]
        instance_arguments = instance["arguments"]

        baud = int(self.system_setup.get("baud", 1000000))
        instance_parameter["BUFFER_SIZE"] = self.system_setup["buffer_size"]
        instance_parameter["MSGID"] = "32'h74697277"
        instance_parameter["TIMEOUT"] = f"32'd{self.system_setup['speed'] // 4}"
        instance_parameter["ClkFrequency"] = self.system_setup["speed"]
        instance_parameter["Baud"] = baud

        return instances
