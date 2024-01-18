from riocore.plugins import PluginBase


class Plugin(PluginBase):
    def setup(self):
        self.NAME = "w5500"
        self.VERILOGS = ["w5500.v"]
        self.PINDEFAULTS = {
            "mosi": {
                "direction": "output",
                "invert": False,
                "pullup": False,
            },
            "miso": {
                "direction": "input",
                "invert": False,
                "pullup": False,
            },
            "sclk": {
                "direction": "output",
                "invert": False,
                "pullup": False,
            },
            "sel": {
                "direction": "output",
                "invert": False,
                "pullup": False,
            },
        }
        self.TYPE = "interface"
        self.OPTIONS = {
            "mac": {
                "default": "AA:AF:FA:CC:E3:1C",
                "type": str,
            },
            "ip": {
                "default": "192.168.10.194",
                "type": str,
            },
            "port": {
                "default": 2390,
                "type": int,
            },
        }

    def gateware_instances(self):
        instances = self.gateware_instances_base()
        instance = instances[self.instances_name]
        instance_predefines = instance["predefines"]
        instance_parameter = instance["parameter"]
        instance_arguments = instance["arguments"]

        instance_parameter["IP_ADDR"] = "{8'd192, 8'd168, 8'd10, 8'd193}"
        instance_parameter["MAC_ADDR"] = "{8'hAA, 8'hAF, 8'hFA, 8'hCC, 8'hE3, 8'h1C}"
        instance_parameter["PORT"] = "2390"

        instance_parameter["BUFFER_SIZE"] = "BUFFER_SIZE"
        instance_parameter["MSGID"] = "32'h74697277"

        spi_clk_speed = 2000000
        divider = self.system_setup["speed"] // spi_clk_speed // 5
        instance_parameter["DIVIDER"] = divider

        # instance_parameter["TIMEOUT"] = f"32'd{self.system_setup['speed'] // 20}"
        instance_parameter["TIMEOUT"] = f"32'd{spi_clk_speed // 4}"

        return instances
