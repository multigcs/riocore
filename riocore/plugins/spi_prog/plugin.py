from riocore.plugins import PluginBase


class Plugin(PluginBase):
    def setup(self):
        self.NAME = "spi_prog"
        self.INFO = "spi interface for host comunication and flash programming"
        self.DESCRIPTION = "for direct connections to Raspberry-PI - supporting flash programming"
        self.KEYWORDS = "interface spi raspberry rpi flash mesa"
        self.ORIGIN = "https://www.fpga4fun.com/SPI2.html"
        self.VERILOGS = ["spi_prog.v"]
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
            "prog": {
                "direction": "input",
                "invert": False,
                "pull": "down",
            },
            "reboot": {
                "direction": "output",
                "invert": False,
                "pull": "down",
            },
            "eeprom_mosi": {
                "direction": "output",
                "invert": False,
                "pull": None,
            },
            "eeprom_miso": {
                "direction": "input",
                "invert": False,
                "pull": None,
                "slew": "fast",
            },
            "eeprom_sclk": {
                "direction": "output",
                "invert": False,
                "pull": None,
            },
            "eeprom_sel": {
                "direction": "output",
                "invert": False,
                "pull": None,
            },
        }
        self.TYPE = "interface"

    def gateware_instances(self):
        instances = self.gateware_instances_base()
        instance = instances[self.instances_name]
        instance_parameter = instance["parameter"]
        instance_parameter["BUFFER_SIZE"] = "BUFFER_SIZE"
        instance_parameter["MSGID"] = "32'h74697277"
        return instances
