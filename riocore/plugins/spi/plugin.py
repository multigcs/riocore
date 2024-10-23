from riocore.plugins import PluginBase


class Plugin(PluginBase):
    def setup(self):
        self.NAME = "spi"
        self.INFO = "spi interface for host comunication"
        self.DESCRIPTION = "for direct connections to Raspberry-PI or over UDB2SPI-Bridges"
        self.KEYWORDS = "interface spi raspberry rpi"
        self.ORIGIN = "https://www.fpga4fun.com/SPI2.html"
        self.VERILOGS = ["spi.v"]
        self.PINDEFAULTS = {
            "mosi": {
                "direction": "input",
                "invert": False,
                "pull": None,
            },
            "miso": {
                "direction": "output",
                "invert": False,
                "pull": None,
                "slew": "fast",
            },
            "sclk": {
                "direction": "input",
                "invert": False,
                "pull": None,
            },
            "sel": {
                "direction": "input",
                "invert": False,
                "pull": None,
            },
        }
        self.TYPE = "interface"

    def gateware_instances(self):
        instances = self.gateware_instances_base()
        instance = instances[self.instances_name]
        instance["predefines"]
        instance_parameter = instance["parameter"]
        instance["arguments"]

        instance_parameter["BUFFER_SIZE"] = "BUFFER_SIZE"
        instance_parameter["MSGID"] = "32'h74697277"

        return instances
