from riocore.plugins import PluginBase


class Plugin(PluginBase):
    def setup(self):
        self.NAME = "spi"
        self.INFO = "spi interface for host comunication"
        self.DESCRIPTION = "for direct connections via SPI"
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
        self.HOST_INTERFACE = "SPI"
        self.OPTIONS = {
            "spitype": {
                "default": "rpi4",
                "type": "select",
                "options": ["rpi4", "rpi5", "generic"],
                "description": "SPI-Type",
            },
            "cs": {
                "default": 0,
                "type": int,
                "min": 0,
                "max": 1,
                "description": "Chip-Select pin on the Host-Side CS0/CS1",
            },
        }
        spitype = self.plugin_setup.get("spitype", self.option_default("spitype", 0))
        if spitype == "rpi5":
            self.HOST_INTERFACE = "SPI_RPI5"
        elif spitype == "generic":
            self.HOST_INTERFACE = "SPI_GENERIC"
        else:
            self.HOST_INTERFACE = "SPI"

    def gateware_instances(self):
        instances = self.gateware_instances_base()
        instance = instances[self.instances_name]
        instance_parameter = instance["parameter"]
        instance_parameter["BUFFER_SIZE_RX"] = "BUFFER_SIZE_RX"
        instance_parameter["BUFFER_SIZE_TX"] = "BUFFER_SIZE_TX"
        instance_parameter["MSGID"] = "32'h74697277"
        return instances
