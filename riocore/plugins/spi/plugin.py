from riocore.plugins import PluginBase


class Plugin(PluginBase):
    def setup(self):
        self.NAME = "spi"
        self.VERILOGS = ["spi.v"]
        self.PINDEFAULTS = {
            "mosi": {
                "direction": "input",
                "invert": False,
                "pullup": False,
            },
            "miso": {
                "direction": "output",
                "invert": False,
                "pullup": False,
            },
            "sclk": {
                "direction": "input",
                "invert": False,
                "pullup": False,
            },
            "sel": {
                "direction": "input",
                "invert": False,
                "pullup": False,
            },
        }
        self.TYPE = "interface"
        self.INFO = "spi interface for host comunication"
        self.DESCRIPTION = "for direct connections to Raspberry-PI or over UDB2SPI-Bridges"

    def gateware_instances(self):
        instances = self.gateware_instances_base()
        instance = instances[self.instances_name]
        instance_predefines = instance["predefines"]
        instance_parameter = instance["parameter"]
        instance_arguments = instance["arguments"]

        instance_parameter["BUFFER_SIZE"] = "BUFFER_SIZE"
        instance_parameter["MSGID"] = "32'h74697277"
        instance_parameter["TIMEOUT"] = f"32'd{self.system_setup['speed'] // 20}"

        return instances
