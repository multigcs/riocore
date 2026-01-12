from riocore.plugins import PluginBase


class Plugin(PluginBase):
    def setup(self):
        self.NAME = "spi"
        self.INFO = "spi interface for host comunication over UDB2SPI-Bridges"
        self.DESCRIPTION = "for UDP connections via UDB2SPI-Bridges"
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
        self.HOST_INTERFACE = "UDP"
        self.OPTIONS = {
            "ip": {
                "default": "192.168.10.194",
                "type": str,
                "description": "IP-Address",
            },
            "mask": {
                "default": "255.255.255.0",
                "type": str,
                "description": "Network-Mask",
            },
            "gw": {
                "default": "192.168.10.1",
                "type": str,
                "description": "Gateway IP-Address",
            },
            "port": {
                "default": 2390,
                "type": int,
                "description": "UDP-Port",
            },
        }

    def gateware_instances(self):
        instances = self.gateware_instances_base()
        instance = instances[self.instances_name]
        instance_parameter = instance["parameter"]
        instance_parameter["BUFFER_SIZE_RX"] = "BUFFER_SIZE_RX"
        instance_parameter["BUFFER_SIZE_TX"] = "BUFFER_SIZE_TX"
        instance_parameter["MSGID"] = "32'h74697277"
        return instances
