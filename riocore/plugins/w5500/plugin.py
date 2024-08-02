from riocore.plugins import PluginBase


class Plugin(PluginBase):
    def setup(self):
        self.NAME = "w5500"
        self.TYPE = "interface"
        self.VERILOGS = ["w5500.v"]
        self.PINDEFAULTS = {
            "mosi": {
                "direction": "output",
                "invert": False,
                "pull": None,
                "slew": "fast",
            },
            "miso": {
                "direction": "input",
                "invert": False,
                "pull": None,
            },
            "sclk": {
                "direction": "output",
                "invert": False,
                "pull": None,
                "slew": "fast",
            },
            "sel": {
                "direction": "output",
                "invert": False,
                "pull": None,
            },
        }
        self.spi_clk_speed = 2000000
        #self.TIMING_CONSTRAINTS = {
        #    "mclk": self.spi_clk_speed,
        #}
        self.OPTIONS = {
            "mac": {
                "default": "AA:AF:FA:CC:E3:1C",
                "type": str,
                "description": "MAC-Address",
            },
            "ip": {
                "default": "192.168.10.194",
                "type": str,
                "description": "IP-Address",
            },
            "port": {
                "default": 2390,
                "type": int,
                "description": "UDP-Port",
            },
        }
        self.INFO = "udp interface for host comunication - experimental"
        self.DESCRIPTION = "w5500 driver for the interface communication over UDP"

    def gateware_instances(self):
        instances = self.gateware_instances_base()
        instance = instances[self.instances_name]
        instance_predefines = instance["predefines"]
        instance_parameter = instance["parameter"]
        instance_arguments = instance["arguments"]

        ip = self.plugin_setup.get("ip", self.option_default("ip"))
        mac = self.plugin_setup.get("mac", self.option_default("mac"))
        port = self.plugin_setup.get("port", self.option_default("port"))

        ipl = ip.split(".")
        macl = mac.split(":")
        instance_parameter["IP_ADDR"] = f"{{8'd{ipl[0]}, 8'd{ipl[1]}, 8'd{ipl[2]}, 8'd{ipl[3]}}}"
        instance_parameter["MAC_ADDR"] = f"{{8'h{macl[0]}, 8'h{macl[1]}, 8'h{macl[2]}, 8'h{macl[3]}, 8'h{macl[4]}, 8'h{macl[5]}}}"
        instance_parameter["PORT"] = port

        instance_parameter["BUFFER_SIZE"] = "BUFFER_SIZE"
        instance_parameter["MSGID"] = "32'h74697277"

        divider = self.system_setup["speed"] // self.spi_clk_speed // 5
        instance_parameter["DIVIDER"] = divider

        # instance_parameter["TIMEOUT"] = f"32'd{self.system_setup['speed'] // 20}"
        instance_parameter["TIMEOUT"] = f"32'd{self.spi_clk_speed // 4}"

        return instances
